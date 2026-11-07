"""Greenhouse Public API Connector."""
import re
from typing import List, Dict, Any, Optional
import httpx
from bs4 import BeautifulSoup

from .base import BaseConnector
from ..models import RawJob


def parse_salary_from_text(text: str) -> tuple[Optional[float], Optional[float], Optional[str]]:
    """Extract salary min, max, and raw string from free-form text."""
    if not text:
        return None, None, None

    # Matches: $160,000 - $240,000 or $160k - $240k or $160k - 240k or $160,000 to $240,000
    range_match = re.search(
        r'\$\s*([0-9]{2,3}k|[0-9]{2,3}(?:,[0-9]{3})*(?:\.[0-9]{2})?)\s*(?:-|–|—|to)\s*\$?\s*([0-9]{2,3}k|[0-9]{2,3}(?:,[0-9]{3})*(?:\.[0-9]{2})?)',
        text,
        re.IGNORECASE
    )
    if range_match:
        raw_min = range_match.group(1).replace(",", "").lower()
        raw_max = range_match.group(2).replace(",", "").lower()
        
        try:
            val_min = float(raw_min.replace("k", "000")) if "k" in raw_min else float(raw_min)
            val_max = float(raw_max.replace("k", "000")) if "k" in raw_max else float(raw_max)
            return val_min, val_max, f"${val_min:,.0f}–${val_max:,.0f} annual salary"
        except ValueError:
            pass

    # Single figure match: $160,000 or $160k base
    single_match = re.search(
        r'\$\s*([0-9]{2,3}(?:,[0-9]{3})*(?:\.[0-9]{2})?|[0-9]{2,3}k)\s*(?:base|minimum|min|per year|annually|annual)',
        text,
        re.IGNORECASE
    )
    if single_match:
        raw_val = single_match.group(1).replace(",", "").lower()
        try:
            val = float(raw_val.replace("k", "000")) if "k" in raw_val else float(raw_val)
            return val, val, f"${val:,.0f} annual base"
        except ValueError:
            pass

    return None, None, None


class GreenhouseConnector(BaseConnector):
    """Crawl jobs from Greenhouse public board API."""

    def __init__(self, timeout: float = 10.0):
        super().__init__(name="greenhouse", timeout=timeout)

    async def fetch_jobs(
        self,
        board_token: str,
        company_name: str,
        client: httpx.AsyncClient,
        **kwargs
    ) -> List[RawJob]:
        """Fetch all postings with content=true for maximum fidelity."""
        url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true"
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
                abs_url = item.get("absolute_url", "").strip()
                if not abs_url:
                    continue

                # Parse location
                loc_obj = item.get("location", {})
                location_name = loc_obj.get("name", "") if isinstance(loc_obj, dict) else str(loc_obj)

                # Parse content HTML
                content_html = item.get("content", "") or ""
                desc_text = ""
                if content_html:
                    try:
                        soup = BeautifulSoup(content_html, "html.parser")
                        desc_text = soup.get_text(separator=" ", strip=True)
                    except Exception:
                        desc_text = re.sub(r'<[^>]+>', ' ', content_html)

                sal_min, sal_max, sal_str = parse_salary_from_text(desc_text)

                jobs.append(RawJob(
                    job_id=f"gh_{board_token}_{job_id}",
                    company=company_name,
                    title=title,
                    url=abs_url,
                    connector=self.name,
                    location_raw=location_name,
                    compensation_raw=sal_str,
                    salary_min=sal_min,
                    salary_max=sal_max,
                    currency="USD",
                    description_text=desc_text,
                    categories={"departments": item.get("departments", []), "offices": item.get("offices", [])},
                    metadata={"board_token": board_token, "updated_at": item.get("updated_at")}
                ))

        except Exception as e:
            # Resilient connector: log or ignore failures for individual endpoints
            pass

        return jobs
