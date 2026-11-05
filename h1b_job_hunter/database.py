"""SQLite database manager for persistent state, deduplication, and cooldown tracking."""
import sqlite3
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any
from urllib.parse import urlparse

from .config import DB_PATH, INITIAL_COOLDOWNS, DEFAULT_COOLDOWN_DAYS
from .models import EvaluatedJob


def normalize_job_url(url: str) -> str:
    """Normalize a job URL while preserving unique job identifier parameters (gh_jid, job_id, etc.)."""
    if not url:
        return ""
    u = url.strip().lower().rstrip("/")
    parsed = urlparse(u)
    if any(k in parsed.query for k in ("gh_jid=", "job_id=", "id=", "jid=")):
        for part in parsed.query.split("&"):
            if any(part.startswith(k) for k in ("gh_jid=", "job_id=", "id=", "jid=")):
                return f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{part}".rstrip("/")
        return u
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")


def normalize_company_name(name: str) -> str:
    """Normalize company name to lowercase, stripped of legal entity suffixes and parentheticals."""
    if not name:
        return ""
    n = str(name).strip().lower()
    # Remove parenthetical info e.g. "Within (formerly Klarity)" -> "within"
    n = re.sub(r'\(.*?\)', '', n).strip()
    # Remove common corporate suffixes
    n = re.sub(r'\b(inc\.?|llc\.?|corp\.?|corporation|technologies|systems|labs?|co\.?|ltd\.?)\b', '', n, flags=re.IGNORECASE).strip()
    # Normalize whitespaces
    n = re.sub(r'\s+', ' ', n)
    return n


class DatabaseManager:
    """Manages SQLite storage for applied records, discovered jobs, and cooldown registries."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = Path(db_path)
        self._applied_companies_cache = None
        self._applied_links_cache = None
        self._cooldown_cache = None
        self.init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _load_caches(self) -> None:
        """Preload applied companies, links, and cooldowns into in-memory sets for O(1) lookups."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT company_norm FROM applied_companies")
            self._applied_companies_cache = {row[0] for row in cursor.fetchall()}

            cursor.execute("SELECT url FROM applied_links")
            self._applied_links_cache = {
                normalize_job_url(row[0]) for row in cursor.fetchall() if row[0]
            }

            cursor.execute("SELECT url FROM discovered_jobs")
            for row in cursor.fetchall():
                if row[0]:
                    self._applied_links_cache.add(normalize_job_url(row[0]))

            cursor.execute("SELECT company_norm, original_name, cooldown_date, cooldown_days, reason FROM cooldown_registry")
            self._cooldown_cache = {
                row[0]: (row[1], row[2], row[3], row[4]) for row in cursor.fetchall()
            }

    def init_db(self) -> None:
        """Create database tables and indexes if they do not exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. applied_companies
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS applied_companies (
                    company_norm TEXT PRIMARY KEY,
                    original_name TEXT,
                    source TEXT,
                    first_seen_at TEXT
                )
            """)
            
            # 2. applied_links
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS applied_links (
                    url TEXT PRIMARY KEY,
                    company TEXT,
                    role TEXT,
                    source TEXT,
                    added_at TEXT
                )
            """)
            
            # 3. discovered_jobs
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS discovered_jobs (
                    job_id TEXT PRIMARY KEY,
                    company TEXT,
                    role TEXT,
                    url TEXT UNIQUE,
                    batch_id TEXT,
                    status TEXT,
                    salary TEXT,
                    location TEXT,
                    role_focus TEXT,
                    scraped_at TEXT,
                    raw_json TEXT
                )
            """)
            
            # 4. cooldown_registry
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cooldown_registry (
                    company_norm TEXT PRIMARY KEY,
                    original_name TEXT,
                    cooldown_date TEXT,
                    cooldown_days INTEGER DEFAULT 60,
                    reason TEXT,
                    created_at TEXT
                )
            """)
            
            # Create indexes for fast lookup
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_applied_links_url ON applied_links (url)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_discovered_jobs_url ON discovered_jobs (url)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_discovered_jobs_batch ON discovered_jobs (batch_id)")
            
            conn.commit()

        # Seed initial cooldowns if not already present
        self._seed_initial_cooldowns()

    def _seed_initial_cooldowns(self) -> None:
        """Seed initial cooldowns for OpenAI, Sierra, and Capital One."""
        # Default cooldown date anchored to current cycle (e.g. 2026-11-01)
        base_date = "2026-11-01"
        for comp_name, days in INITIAL_COOLDOWNS.items():
            norm = normalize_company_name(comp_name)
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR IGNORE INTO cooldown_registry 
                    (company_norm, original_name, cooldown_date, cooldown_days, reason, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    norm,
                    comp_name.title(),
                    base_date,
                    days,
                    "Application frequency limit / cooldown active",
                    datetime.utcnow().isoformat()
                ))
                conn.commit()

    def is_company_on_cooldown(self, company: str, check_date: Optional[datetime] = None) -> Tuple[bool, Optional[str]]:
        """
        Check if company is currently within its cooldown window (cooldown_date + cooldown_days).
        """
        if not company:
            return False, None
        
        if self._cooldown_cache is None:
            self._load_caches()

        norm = normalize_company_name(company)
        now = check_date or datetime.utcnow()

        for cd_norm, (orig_name, cd_date_str, days, reason) in self._cooldown_cache.items():
            if norm == cd_norm or cd_norm in norm:
                try:
                    c_date = datetime.fromisoformat(cd_date_str.split(" ")[0])
                except Exception:
                    c_date = datetime.strptime(cd_date_str.split(" ")[0], "%Y-%m-%d")
                
                expiry = c_date + timedelta(days=days)
                if now < expiry:
                    return True, f"Cooldown active until {expiry.strftime('%Y-%m-%d')} ({reason})"

        return False, None

    def is_company_applied(self, company: str) -> bool:
        """Check if company name has already been recorded in applied_companies."""
        if not company:
            return False
        if self._applied_companies_cache is None:
            self._load_caches()
        norm = normalize_company_name(company)
        return norm in self._applied_companies_cache

    def is_link_applied_or_discovered(self, url: str) -> bool:
        """Check if posting URL has already been logged in applied_links or discovered_jobs."""
        if not url:
            return False
        if self._applied_links_cache is None:
            self._load_caches()
        clean_url = normalize_job_url(url)
        return clean_url in self._applied_links_cache

    def add_applied_company(self, company: str, source: str) -> None:
        """Add normalized company to applied_companies."""
        if not company:
            return
        norm = normalize_company_name(company)
        if not norm:
            return
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO applied_companies (company_norm, original_name, source, first_seen_at)
                VALUES (?, ?, ?, ?)
            """, (norm, str(company).strip(), source, datetime.utcnow().isoformat()))
            conn.commit()

    def add_applied_link(self, url: str, company: str, role: str, source: str) -> None:
        """Add application URL to applied_links."""
        if not url:
            return
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO applied_links (url, company, role, source, added_at)
                VALUES (?, ?, ?, ?, ?)
            """, (url.strip(), company, role, source, datetime.utcnow().isoformat()))
            conn.commit()

    def add_applied_batch(self, companies: List[Tuple[str, str]], links: List[Tuple[str, str, str, str]]) -> Tuple[int, int]:
        """Insert batch of companies and links within a single transaction for maximum performance."""
        now = datetime.utcnow().isoformat()
        comp_count = 0
        link_count = 0
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            comp_rows = []
            for comp, src in companies:
                norm = normalize_company_name(comp)
                if norm:
                    comp_rows.append((norm, str(comp).strip(), src, now))
                    
            cursor.executemany("""
                INSERT OR IGNORE INTO applied_companies (company_norm, original_name, source, first_seen_at)
                VALUES (?, ?, ?, ?)
            """, comp_rows)
            comp_count = len(comp_rows)
            
            link_rows = []
            for url, comp, role, src in links:
                if url:
                    link_rows.append((url.strip(), comp or "", role or "", src, now))
                    
            cursor.executemany("""
                INSERT OR IGNORE INTO applied_links (url, company, role, source, added_at)
                VALUES (?, ?, ?, ?, ?)
            """, link_rows)
            link_count = len(link_rows)
            
            conn.commit()
            self._applied_companies_cache = None
            self._applied_links_cache = None
            
        return comp_count, link_count

    def record_discovered_jobs(self, jobs: List[EvaluatedJob], batch_id: str) -> int:
        """Record exported jobs in discovered_jobs to prevent future duplication."""
        count = 0
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for j in jobs:
                job_id = f"{normalize_company_name(j.company)}_{hash(j.job_posting_link)}"
                cursor.execute("""
                    INSERT OR REPLACE INTO discovered_jobs 
                    (job_id, company, role, url, batch_id, status, salary, location, role_focus, scraped_at, raw_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    job_id,
                    j.company,
                    j.role,
                    j.job_posting_link,
                    batch_id,
                    j.status,
                    j.salary,
                    j.location,
                    j.role_focus,
                    datetime.utcnow().isoformat(),
                    ""
                ))
                count += 1
            conn.commit()
        return count

    def set_cooldown(self, company: str, cooldown_date: str, days: int = DEFAULT_COOLDOWN_DAYS, reason: str = "Application limit") -> None:
        """Set or update cooldown for a company."""
        norm = normalize_company_name(company)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO cooldown_registry 
                (company_norm, original_name, cooldown_date, cooldown_days, reason, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (norm, company, cooldown_date, days, reason, datetime.utcnow().isoformat()))
            conn.commit()

    def remove_cooldown(self, company: str) -> bool:
        """Remove a company from cooldown."""
        norm = normalize_company_name(company)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cooldown_registry WHERE company_norm = ?", (norm,))
            conn.commit()
            return cursor.rowcount > 0

    def get_cooldowns(self) -> List[Dict[str, Any]]:
        """List all cooldown registry entries."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM cooldown_registry ORDER BY cooldown_date DESC")
            return [dict(r) for r in cursor.fetchall()]

    def get_stats(self) -> Dict[str, Any]:
        """Return aggregate database statistics."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT count(*) FROM applied_companies")
            comp_cnt = cursor.fetchone()[0]
            
            cursor.execute("SELECT count(*) FROM applied_links")
            link_cnt = cursor.fetchone()[0]
            
            cursor.execute("SELECT count(*) FROM discovered_jobs")
            disc_cnt = cursor.fetchone()[0]
            
            cursor.execute("SELECT count(*) FROM cooldown_registry")
            cd_cnt = cursor.fetchone()[0]
            
            return {
                "applied_companies_count": comp_cnt,
                "applied_links_count": link_cnt,
                "discovered_jobs_count": disc_cnt,
                "cooldown_companies_count": cd_cnt
            }
