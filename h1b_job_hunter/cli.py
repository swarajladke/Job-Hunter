"""CLI interface for h1b-job-hunter."""
import argparse
import asyncio
import sys
from pathlib import Path
from datetime import datetime

from .config import DB_PATH, DEFAULT_TRACKERS
from .database import DatabaseManager, normalize_company_name
from .ingestion import TrackerIngestion
from .pipeline import JobHunterPipeline


def format_table(headers: list, rows: list) -> str:
    """Simple ASCII table formatter."""
    if not rows:
        return "No records found."
    widths = [len(h) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            widths[i] = max(widths[i], len(str(val)))
    header_str = " | ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
    sep_str = "-+-".join("-" * widths[i] for i in range(len(headers)))
    row_strs = [" | ".join(str(val).ljust(widths[i]) for i, val in enumerate(row)) for row in rows]
    return f"{header_str}\n{sep_str}\n" + "\n".join(row_strs)


def main():
    parser = argparse.ArgumentParser(
        prog="h1b-job-hunter",
        description="Autonomous H-1B Job Discovery, Filtering, Evaluation & Deduplication Pipeline"
    )
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # Command: run / search
    run_parser = subparsers.add_parser("run", aliases=["search"], help="Execute daily job discovery pipeline")
    run_parser.add_argument("-n", "--limit", type=int, default=50, help="Number of verified roles to export (default: 50)")
    run_parser.add_argument("-o", "--output", type=str, default=None, help="Output Excel file path")
    run_parser.add_argument("--append", action="store_true", help="Append evaluated jobs to existing output Excel file instead of overwriting")
    run_parser.add_argument("--allow-existing-companies", action="store_true", help="Allow new roles at previously applied companies")
    run_parser.add_argument("--concurrency", type=int, default=15, help="Async request concurrency limit")

    # Command: sync
    sync_parser = subparsers.add_parser("sync", help="Ingest tracker files into SQLite database")
    sync_parser.add_argument("files", nargs="*", default=None, help="Optional Excel file paths to ingest")

    # Command: stats
    stats_parser = subparsers.add_parser("stats", help="Show database metrics and cooldown registry")

    # Command: cooldown
    cd_parser = subparsers.add_parser("cooldown", help="Manage company cooldown registry")
    cd_parser.add_argument("--add", type=str, help="Add company to cooldown")
    cd_parser.add_argument("--days", type=int, default=60, help="Cooldown duration in days (default: 60)")
    cd_parser.add_argument("--reason", type=str, default="Application limit reached", help="Reason for cooldown")
    cd_parser.add_argument("--remove", type=str, help="Remove company from cooldown")
    cd_parser.add_argument("--list", action="store_true", help="List all cooldown entries")

    args = parser.parse_args()

    if not args.command or args.command in ("run", "search"):
        limit = getattr(args, "limit", 50)
        out_path = Path(args.output) if getattr(args, "output", None) else None
        allow_existing = getattr(args, "allow_existing_companies", False)
        concurrency = getattr(args, "concurrency", 15)
        append_mode = getattr(args, "append", False)

        print("\n" + "="*70)
        print("  H-1B JOB HUNTER: AUTONOMOUS AI ENGINEERING DISCOVERY ENGINE")
        print("="*70)
        print(f"[*] Target Roles Limit:     {limit}")
        print(f"[*] Export Mode:            {'Append to existing Excel' if append_mode else 'Overwrite Excel'}")
        print(f"[*] Deduplication Mode:     {'Strict (Reject applied companies)' if not allow_existing else 'Permissive (Allow applied companies with new URLs)'}")
        print(f"[*] Concurrency Limit:      {concurrency}")
        print(f"[*] Database Path:          {DB_PATH}")
        print("="*70 + "\n")

        pipeline = JobHunterPipeline(
            db_path=DB_PATH,
            allow_existing_companies=allow_existing,
            concurrency=concurrency
        )

        async def _execute():
            jobs, metrics, saved_path = await pipeline.run(target_count=limit, output_file=out_path, append=append_mode)
            
            duration = (metrics.completed_at - metrics.started_at).total_seconds() if metrics.completed_at else 0
            
            print("\n" + "="*70)
            print("  PIPELINE EXECUTION TELEMETRY & RESULTS")
            print("="*70)
            print(f"  Boards Queried:           {metrics.boards_queried}")
            print(f"  Raw Jobs Discovered:      {metrics.raw_jobs_scraped}")
            print(f"  Dropped via Cooldown:     {metrics.cooldown_dropped}")
            print(f"  Dropped via Deduplication: {metrics.dedup_dropped}")
            print(f"  Dropped via Non-AI Title: {metrics.title_rejected}")
            print(f"  Dropped via Seniority:    {metrics.seniority_rejected}")
            print(f"  Dropped via Non-US Geo:   {metrics.geo_rejected}")
            print(f"  Dropped via Clearance:    {metrics.clearance_rejected}")
            print(f"  Dropped Below $150k Floor: {metrics.salary_rejected}")
            print(f"  Live Links Verified:      {metrics.verified_jobs} (Failed: {metrics.link_failed})")
            print(f"  Exported Verified Roles:  {metrics.exported_jobs}")
            print(f"  Execution Time:           {duration:.2f}s")
            print(f"  Output Excel File:        {saved_path.resolve()}")
            print("="*70 + "\n")

            if jobs:
                print(f"Sample First 5 Discovered & Evaluated Roles:\n")
                sample_rows = [
                    [j.company[:18], j.role[:30], j.location[:20], j.salary[:22], j.role_focus[:25]]
                    for j in jobs[:5]
                ]
                print(format_table(["Company", "Role", "Location", "Salary", "Role Focus"], sample_rows))
                print("\n")

        asyncio.run(_execute())

    elif args.command == "sync":
        db = DatabaseManager(DB_PATH)
        ingestion = TrackerIngestion(db)
        files = [Path(f) for f in args.files] if args.files else None
        res = ingestion.ingest_trackers(files)
        print("\n" + "="*50)
        print("  TRACKER INGESTION REPORT")
        print("="*50)
        for f in res["files"]:
            print(f"  {Path(f['path']).name}: {f['companies_ingested']} companies, {f['links_ingested']} links ({f['status']})")
        print("-" * 50)
        print(f"  Applied Companies in DB: {res['db_stats']['applied_companies_count']}")
        print(f"  Applied Links in DB:     {res['db_stats']['applied_links_count']}")
        print(f"  Cooldown Registries:     {res['db_stats']['cooldown_companies_count']}")
        print("="*50 + "\n")

    elif args.command == "stats":
        db = DatabaseManager(DB_PATH)
        stats = db.get_stats()
        cooldowns = db.get_cooldowns()
        print("\n" + "="*50)
        print("  DATABASE & COOLDOWN STATUS")
        print("="*50)
        print(f"  Applied Companies:  {stats['applied_companies_count']}")
        print(f"  Applied Links:      {stats['applied_links_count']}")
        print(f"  Discovered Jobs:    {stats['discovered_jobs_count']}")
        print(f"  Active Cooldowns:   {stats['cooldown_companies_count']}")
        print("\nCooldown Registry Entries:")
        cd_rows = [[c["original_name"], c["cooldown_date"], f"{c['cooldown_days']} days", c["reason"][:30]] for c in cooldowns]
        print(format_table(["Company", "Cooldown Date", "Window", "Reason"], cd_rows))
        print("="*50 + "\n")

    elif args.command == "cooldown":
        db = DatabaseManager(DB_PATH)
        if args.add:
            today_str = datetime.utcnow().strftime("%Y-%m-%d")
            db.set_cooldown(args.add, cooldown_date=today_str, days=args.days, reason=args.reason)
            print(f"[+] Added {args.add} to cooldown ({args.days} days from {today_str})")
        elif args.remove:
            removed = db.remove_cooldown(args.remove)
            if removed:
                print(f"[-] Removed {args.remove} from cooldown.")
            else:
                print(f"[!] Company {args.remove} not found in cooldown registry.")
        elif args.list or True:
            cooldowns = db.get_cooldowns()
            cd_rows = [[c["original_name"], c["cooldown_date"], f"{c['cooldown_days']} days", c["reason"][:30]] for c in cooldowns]
            print(format_table(["Company", "Cooldown Date", "Window", "Reason"], cd_rows))


if __name__ == "__main__":
    main()

