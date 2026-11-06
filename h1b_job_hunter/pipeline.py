"""Orchestration pipeline for discovery, filtering, link verification, evaluation, and export."""
import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import httpx

from .models import RawJob, FilterResult, EvaluatedJob, RunMetrics
from .config import DB_PATH, DEFAULT_TRACKERS, BLOCKED_COMPANIES
from .registry import KNOWN_ATS_BOARDS
from .database import DatabaseManager, normalize_company_name
from .ingestion import TrackerIngestion
from .connectors import AshbyConnector, GreenhouseConnector, LeverConnector, WorkdayConnector
from .filters import JobFilterEngine
from .verifier import LinkVerifier
from .evaluator import CandidateEvaluator
from .exporter import ExcelExporter


class JobHunterPipeline:
    """End-to-end execution pipeline."""

    def __init__(
        self,
        db_path: Path = DB_PATH,
        allow_existing_companies: bool = False,
        concurrency: int = 15
    ):
        self.db = DatabaseManager(db_path)
        self.allow_existing_companies = allow_existing_companies
        self.concurrency = concurrency
        
        # Connectors
        self.ashby = AshbyConnector(timeout=7.0)
        self.greenhouse = GreenhouseConnector(timeout=7.0)
        self.lever = LeverConnector(timeout=7.0)
        self.workday = WorkdayConnector(timeout=7.0)
        
        # Engine components
        self.filter_engine = JobFilterEngine(self.db, allow_existing_companies=allow_existing_companies)
        self.verifier = LinkVerifier(concurrency=concurrency, timeout=6.0)
        self.evaluator = CandidateEvaluator()

    async def run(
        self,
        target_count: int = 50,
        output_file: Optional[Path] = None,
        batch_id: Optional[str] = None,
        append: bool = False
    ) -> tuple[List[EvaluatedJob], RunMetrics, Path]:
        """Execute full pipeline run."""
        metrics = RunMetrics()
        now_str = datetime.utcnow().strftime("%Y-%m-%d")
        batch = batch_id or f"BATCH-{now_str}"
        
        # 1. Ensure trackers are ingested
        print("[1/6] Ingesting historical trackers into SQLite...", flush=True)
        ingestion = TrackerIngestion(self.db)
        ingestion.ingest_trackers()

        # 2. Gather raw jobs across all known ATS boards concurrently
        print(f"[2/6] Concurrently scraping {len(KNOWN_ATS_BOARDS)} target ATS boards (Ashby, Greenhouse, Lever, Workday)...", flush=True)
        raw_jobs: List[RawJob] = []
        poc_map: Dict[str, str] = {}
        
        sem = asyncio.Semaphore(self.concurrency)
        async with httpx.AsyncClient(follow_redirects=True) as client:
            
            async def fetch_board(ats: str, token: str, comp_name: str, cat: str, tier: str, poc: str, *args):
                async with sem:
                    poc_map[normalize_company_name(comp_name)] = poc
                    try:
                        if ats == "ashby":
                            return await self.ashby.fetch_jobs(token, comp_name, client)
                        elif ats == "greenhouse":
                            return await self.greenhouse.fetch_jobs(token, comp_name, client)
                        elif ats == "lever":
                            return await self.lever.fetch_jobs(token, comp_name, client)
                        elif ats == "workday":
                            site = args[0] if args else "External"
                            return await self.workday.fetch_jobs(token, comp_name, client, site=site)
                    except Exception:
                        pass
                    return []

            # Filter out blocked companies (e.g. Cloudflare, Databricks)
            active_boards = [
                b for b in KNOWN_ATS_BOARDS
                if normalize_company_name(b[2]) not in BLOCKED_COMPANIES
                and b[1].lower() not in BLOCKED_COMPANIES
            ]

            tasks = [fetch_board(*board_spec) for board_spec in active_boards]
            metrics.boards_queried = len(tasks)
            board_results = await asyncio.gather(*tasks, return_exceptions=True)

            for res in board_results:
                if isinstance(res, list):
                    raw_jobs.extend(res)

        metrics.raw_jobs_scraped = len(raw_jobs)
        print(f"[3/6] Scraped {metrics.raw_jobs_scraped} raw postings across target companies. Applying filters...", flush=True)

        # 3. Filter raw jobs
        filtered_jobs: List[RawJob] = []
        for job in raw_jobs:
            f_res = self.filter_engine.evaluate(job)
            if f_res.is_passed:
                filtered_jobs.append(job)
            else:
                reason = f_res.rejection_reason or ""
                if "COOLDOWN" in reason: metrics.cooldown_dropped += 1
                elif "DUPLICATE" in reason: metrics.dedup_dropped += 1
                elif "TITLE" in reason: metrics.title_rejected += 1
                elif "SENIORITY" in reason: metrics.seniority_rejected += 1
                elif "LOCATION" in reason: metrics.geo_rejected += 1
                elif "CLEARANCE" in reason: metrics.clearance_rejected += 1
                elif "SALARY" in reason: metrics.salary_rejected += 1

        print(f"[4/6] {len(filtered_jobs)} candidate AI roles passed strict filters. Verifying direct application links...", flush=True)

        # 4. Verify links asynchronously (100% working live links)
        verified_jobs: List[RawJob] = []
        async with httpx.AsyncClient(follow_redirects=True) as client:
            
            async def verify_single(j: RawJob):
                is_valid, msg = await self.verifier.verify_url(client, j.url)
                if is_valid:
                    return j
                return None

            v_tasks = [verify_single(j) for j in filtered_jobs]
            v_results = await asyncio.gather(*v_tasks, return_exceptions=True)
            for res in v_results:
                if isinstance(res, RawJob):
                    verified_jobs.append(res)
                else:
                    metrics.link_failed += 1

        metrics.verified_jobs = len(verified_jobs)
        print(f"[5/6] {metrics.verified_jobs} direct links verified live (zero 404s). Evaluating candidate fit for Rishabh Goyal...", flush=True)

        # 5. Evaluate verified jobs against Rishabh Goyal persona
        MAX_ROLES_PER_COMPANY = 2
        evaluated: List[EvaluatedJob] = []
        company_counts: Dict[str, int] = {}

        def is_fde(title: str) -> bool:
            t = (title or "").lower()
            return "forward deployed" in t or "fde" in t

        # Strict FDE ratio: 5 to 10 out of 50 (10% to 20% max)
        max_fde = min(10, max(5, int(target_count * 0.20))) if target_count <= 50 else int(target_count * 0.20)
        current_fde = 0
        company_fde_counts: Dict[str, int] = {}
        MAX_FDE_PER_COMPANY = 2

        def can_add_job(j: RawJob, company_cap: int) -> bool:
            nonlocal current_fde
            c_norm = normalize_company_name(j.company)
            if company_counts.get(c_norm, 0) >= company_cap:
                return False
            if is_fde(j.title):
                if current_fde >= max_fde:
                    return False
                if company_fde_counts.get(c_norm, 0) >= MAX_FDE_PER_COMPANY:
                    return False
            return True

        def add_job(j: RawJob):
            nonlocal current_fde
            c_norm = normalize_company_name(j.company)
            poc_info = poc_map.get(c_norm)
            eval_job = self.evaluator.evaluate_job(j, batch_id=batch, poc_override=poc_info)
            evaluated.append(eval_job)
            company_counts[c_norm] = company_counts.get(c_norm, 0) + 1
            if is_fde(j.title):
                current_fde += 1
                company_fde_counts[c_norm] = company_fde_counts.get(c_norm, 0) + 1

        # Split verified jobs: prioritize unapplied companies (0 prior applications)
        unapplied_jobs: List[RawJob] = []
        applied_company_jobs: List[RawJob] = []

        for j in verified_jobs:
            if not self.db.is_company_applied(j.company):
                unapplied_jobs.append(j)
            else:
                applied_company_jobs.append(j)

        # Stage 1: Prioritize companies with 0 prior applications in tracking sheets
        for j in unapplied_jobs:
            if can_add_job(j, MAX_ROLES_PER_COMPANY):
                add_job(j)
                if len(evaluated) >= target_count:
                    break

        # Stage 2: Fall back to previously applied companies (only if allow_existing_companies is True),
        # strictly enforcing MAX_ROLES_PER_COMPANY = 2
        if len(evaluated) < target_count and self.allow_existing_companies:
            for j in applied_company_jobs:
                if can_add_job(j, MAX_ROLES_PER_COMPANY):
                    add_job(j)
                    if len(evaluated) >= target_count:
                        break

        # Stage 3: If target count is not yet reached, fill progressively (up to 5, 7, 10, 15, then 20 roles per company)
        # to guarantee the full target verified roles while strictly preventing single-company flooding
        if len(evaluated) < target_count:
            all_remaining = unapplied_jobs + (applied_company_jobs if self.allow_existing_companies else [])
            for cap_limit in (5, 7, 10, 15, 20):
                for j in all_remaining:
                    if j.url not in [e.job_posting_link for e in evaluated]:
                        if can_add_job(j, cap_limit):
                            add_job(j)
                            if len(evaluated) >= target_count:
                                break
                if len(evaluated) >= target_count:
                    break

        # 6. Export to Excel
        if not output_file:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            target_path = Path.cwd() / f"h1b_verified_ai_roles_{timestamp}.xlsx"
        else:
            target_path = Path(output_file)

        action_verb = "Appending" if append else "Exporting"
        print(f"[6/6] {action_verb} {len(evaluated)} evaluated roles to Excel ({target_path.name})...", flush=True)
        ExcelExporter.export(evaluated, target_path, append=append)
        metrics.exported_jobs = len(evaluated)

        # 7. Record in SQLite discovered_jobs
        self.db.record_discovered_jobs(evaluated, batch_id=batch)
        metrics.completed_at = datetime.utcnow()

        return evaluated, metrics, target_path
