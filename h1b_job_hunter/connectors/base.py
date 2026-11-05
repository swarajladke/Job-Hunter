"""Base connector interface for job board crawlers."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import httpx

from ..models import RawJob


class BaseConnector(ABC):
    """Abstract base class for all job board and career portal connectors."""

    def __init__(self, name: str, timeout: float = 10.0):
        self.name = name
        self.timeout = timeout

    @abstractmethod
    async def fetch_jobs(
        self,
        board_token: str,
        company_name: str,
        client: httpx.AsyncClient,
        **kwargs
    ) -> List[RawJob]:
        """Fetch raw job postings for a company board."""
        pass
