"""Ashby Public API Connector."""
from typing import List, Dict, Any, Optional
import httpx
from bs4 import BeautifulSoup

from .base import BaseConnector
from .greenhouse import parse_salary_from_text
from ..models import RawJob


class AshbyConnector(BaseConnector):
    """Crawl jobs from Ashby posting API."""

    def __init__(self, timeout: float = 10.0):
        super().__init__(name="ashby", timeout=timeout)

    async def fetch_jobs(
        self,
        board_token: str,
        company_name: str,
        client: httpx.AsyncClient,
        **kwargs
    ) -> List[RawJob]:
        """Fetch all postings with structured compensation parsing."""
        url = f"https://api.ashbyhq.com/posting-api/job-board/{board_token}"
        jobs: List[RawJob] = []

        try:
            resp = await client.get(url, timeout=self.timeout)
            if resp.status_code != 200:
                return jobs

            data = resp.json()
            raw_list = data.get("jobs", [])

            for item in raw_list:
                job_id = str(item.get("id", ""))
                title = item.get("title", "").strip()
                job_url = item.get("jobUrl", "").strip()
                if not job_url:
                    continue

                location_name = item.get("locationName", "")
                dept = item.get("department", "")

                # 1. Structured compensation from Ashby
                comp = item.get("compensation") or {}
                comp_min = comp.get("min")
                comp_max = comp.get("max")
                currency = comp.get("currency", "USD")
                comp_summary = comp.get("summary")

                sal_min: Optional[float] = None
                sal_max: Optional[float] = None
                sal_str: Optional[str] = None

                if comp_min is not None:
                    try:
                        sal_min = float(comp_min)
                    except (ValueError, TypeError):
                        pass

                if comp_max is not None:
                    try:
                        sal_max = float(comp_max)
                    except (ValueError, TypeError):
                        pass

                if comp_summary:
                    sal_str = comp_summary
                elif sal_min and sal_max:
                    sal_str = f"${sal_min:,.0f}–${sal_max:,.0f} annual salary"
                elif sal_min:
                    sal_str = f"${sal_min:,.0f}+ annual salary"

                # Parse description text if provided
                desc_html = item.get("descriptionHtml", "") or ""
                desc_text = item.get("descriptionPlain", "") or ""
                if not desc_text and desc_html:
                    try:
                        soup = BeautifulSoup(desc_html, "html.parser")
                        desc_text = soup.get_text(separator=" ", strip=True)
                    except Exception:
                        desc_text = desc_html

                # Fallback salary extraction from description if structured comp was missing
                if sal_min is None and desc_text:
                    parsed_min, parsed_max, parsed_str = parse_salary_from_text(desc_text)
                    if parsed_min:
                        sal_min = parsed_min
                        sal_max = parsed_max
                        sal_str = parsed_str

                jobs.append(RawJob(
                    job_id=f"ashby_{board_token}_{job_id}",
                    company=company_name,
                    title=title,
                    url=job_url,
                    connector=self.name,
                    location_raw=location_name,
                    compensation_raw=sal_str,
                    salary_min=sal_min,
                    salary_max=sal_max,
                    currency=currency or "USD",
                    description_text=desc_text,
                    categories={"department": dept},
                    metadata={"org_slug": board_token, "published_at": item.get("publishedAt")}
                ))

        except Exception:
            pass

        return jobs
