"""Lever Public API Connector."""
from typing import List, Dict, Any, Optional
import httpx

from .base import BaseConnector
from .greenhouse import parse_salary_from_text
from ..models import RawJob


class LeverConnector(BaseConnector):
    """Crawl jobs from Lever posting API."""

    def __init__(self, timeout: float = 10.0):
        super().__init__(name="lever", timeout=timeout)

    async def fetch_jobs(
        self,
        board_token: str,
        company_name: str,
        client: httpx.AsyncClient,
        **kwargs
    ) -> List[RawJob]:
        """Fetch all postings with JSON mode."""
        url = f"https://api.lever.co/v0/postings/{board_token}?mode=json"
        jobs: List[RawJob] = []

        try:
            resp = await client.get(url, timeout=self.timeout)
            if resp.status_code != 200:
                return jobs

            data = resp.json()
            if not isinstance(data, list):
                return jobs

            for item in data:
                job_id = str(item.get("id", ""))
                title = item.get("text", "").strip()
                hosted_url = item.get("hostedUrl", "").strip()
                if not hosted_url:
                    continue

                categories = item.get("categories", {}) or {}
                location_name = categories.get("location", "")
                team = categories.get("team", "")

                desc_plain = item.get("descriptionPlain", "") or ""
                additional = item.get("additionalPlain", "") or ""
                full_text = f"{desc_plain}\n{additional}".strip()

                # Salary range
                sal_min, sal_max, sal_str = parse_salary_from_text(full_text)
                
                # Check salaryRange if structured in Lever
                salary_range = item.get("salaryRange", {})
                if isinstance(salary_range, dict) and salary_range.get("min"):
                    try:
                        s_min = float(salary_range.get("min"))
                        s_max = float(salary_range.get("max", s_min))
                        sal_min, sal_max = s_min, s_max
                        sal_str = f"${sal_min:,.0f}–${sal_max:,.0f} annual salary"
                    except (ValueError, TypeError):
                        pass

                jobs.append(RawJob(
                    job_id=f"lever_{board_token}_{job_id}",
                    company=company_name,
                    title=title,
                    url=hosted_url,
                    connector=self.name,
                    location_raw=location_name,
                    compensation_raw=sal_str,
                    salary_min=sal_min,
                    salary_max=sal_max,
                    currency="USD",
                    description_text=full_text,
                    categories=categories,
                    metadata={"site_name": board_token, "created_at": item.get("createdAt")}
                ))

        except Exception:
            pass

        return jobs
