"""Playwright scraper for dynamic JavaScript-rendered career portals."""
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup

from .base import BaseConnector
from .greenhouse import parse_salary_from_text
from ..models import RawJob


class PlaywrightScraper(BaseConnector):
    """Headless browser crawler for JS-rendered career pages."""

    def __init__(self, timeout: float = 15.0):
        super().__init__(name="playwright", timeout=timeout)

    async def fetch_jobs(
        self,
        board_token: str,
        company_name: str,
        client: Any = None,
        portal_url: Optional[str] = None,
        **kwargs
    ) -> List[RawJob]:
        """Fetch jobs via Playwright Chromium browser."""
        jobs: List[RawJob] = []
        if not portal_url:
            return jobs

        try:
            from playwright.async_api import async_playwright
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
                )
                try:
                    await page.goto(portal_url, wait_until="domcontentloaded", timeout=int(self.timeout * 1000))
                    # Wait briefly for dynamic elements
                    await page.wait_for_timeout(2000)
                    
                    # Extract links containing job or careers
                    links = await page.query_selector_all("a[href*='/job/'], a[href*='/jobs/'], a[href*='/careers/']")
                    for link in links[:25]:
                        href = await link.get_attribute("href")
                        text = await link.inner_text()
                        if href and text and len(text.strip()) > 3:
                            abs_href = href if href.startswith("http") else f"{portal_url.rstrip('/')}/{href.lstrip('/')}"
                            jobs.append(RawJob(
                                job_id=f"pw_{hash(abs_href)}",
                                company=company_name,
                                title=text.strip(),
                                url=abs_href,
                                connector=self.name,
                                location_raw="USA"
                            ))
                finally:
                    await browser.close()
        except Exception:
            pass

        return jobs
