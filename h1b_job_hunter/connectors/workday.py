"""Workday CXS JSON API Connector."""
from typing import List, Dict, Any, Optional
import httpx

from .base import BaseConnector
from .greenhouse import parse_salary_from_text
from ..models import RawJob


class WorkdayConnector(BaseConnector):
    """Crawl jobs from Workday unauthenticated CXS JSON API."""

    def __init__(self, timeout: float = 2.5):
        super().__init__(name="workday", timeout=timeout)

    async def fetch_jobs(
        self,
        board_token: str,
        company_name: str,
        client: httpx.AsyncClient,
        site: str = "External",
        search_text: str = "AI Engineer",
        cluster: str = "wd5",
        **kwargs
    ) -> List[RawJob]:
        """Query Workday CXS search endpoint."""
        tenant = board_token
        url = f"https://{tenant}.{cluster}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }
        payload = {
            "appliedFacets": {},
            "limit": 20,
            "offset": 0,
            "searchText": search_text
        }
        jobs: List[RawJob] = []

        # Try wd5, wd1, wd3 clusters if first fails
        clusters_to_try = [cluster] + [c for c in ["wd1", "wd3", "wd5"] if c != cluster]
        
        for c in clusters_to_try:
            req_url = f"https://{tenant}.{c}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs"
            try:
                resp = await client.post(req_url, json=payload, headers=headers, timeout=self.timeout)
                if resp.status_code == 200:
                    data = resp.json()
                    job_postings = data.get("jobPostings", [])
                    
                    for jp in job_postings:
                        ext_path = jp.get("externalPath", "")
                        title = jp.get("title", "").strip()
                        bullet_fields = jp.get("bulletFields", [])
                        loc = jp.get("locationsText", "") or (bullet_fields[0] if bullet_fields else "")
                        
                        # Build absolute direct URL
                        job_url = f"https://{tenant}.{c}.myworkdayjobs.com/en-US/{tenant}/{site}{ext_path}"
                        job_id = ext_path.split("/")[-1] if ext_path else f"wd_{hash(title)}"
                        
                        jobs.append(RawJob(
                            job_id=f"wd_{tenant}_{job_id}",
                            company=company_name,
                            title=title,
                            url=job_url,
                            connector=self.name,
                            location_raw=loc,
                            metadata={"tenant": tenant, "site": site, "cluster": c}
                        ))
                    return jobs
            except Exception:
                # Connection resets or WAF blocks on specific environments
                continue

        return jobs
