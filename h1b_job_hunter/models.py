"""Data models for the H-1B Job Discovery & Deduplication Engine."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List


@dataclass
class RawJob:
    """Raw job posting retrieved from an ATS or career site."""
    job_id: str
    company: str
    title: str
    url: str
    connector: str
    location_raw: Optional[str] = None
    compensation_raw: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    currency: Optional[str] = "USD"
    description_text: Optional[str] = None
    categories: Dict[str, Any] = field(default_factory=dict)
    scraped_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FilterResult:
    """Filter evaluation result for a job posting."""
    job: RawJob
    is_passed: bool
    rejection_reason: Optional[str] = None
    salary_passed: bool = False
    title_matched: Optional[str] = None
    geo_passed: bool = False
    clearance_passed: bool = False
    dedup_passed: bool = False
    cooldown_passed: bool = False


@dataclass
class EvaluatedJob:
    """Fully evaluated job matching the 15-column Excel schema."""
    company: str
    role: str
    job_posting_link: str
    poc: str
    status: str
    location: str
    salary: str
    h1b_status: str
    applied_date: Optional[str]
    notes: str
    role_focus: str
    salary_review: str
    qualification_review: str
    resume_fit: str
    gaps_and_restrictions: str
    
    # Internal metadata
    score: float = 0.0
    connector: str = ""
    discovered_at: datetime = field(default_factory=datetime.utcnow)

    def to_row(self) -> List[Any]:
        """Convert to 15-column list matching exact Excel schema."""
        return [
            self.company,
            self.role,
            self.job_posting_link,
            self.poc,
            self.status,
            self.location,
            self.salary,
            self.h1b_status,
            self.applied_date,
            self.notes,
            self.role_focus,
            self.salary_review,
            self.qualification_review,
            self.resume_fit,
            self.gaps_and_restrictions
        ]


@dataclass
class RunMetrics:
    """Execution telemetry and metrics."""
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    boards_queried: int = 0
    raw_jobs_scraped: int = 0
    dedup_dropped: int = 0
    cooldown_dropped: int = 0
    title_rejected: int = 0
    seniority_rejected: int = 0
    geo_rejected: int = 0
    clearance_rejected: int = 0
    salary_rejected: int = 0
    link_failed: int = 0
    verified_jobs: int = 0
    exported_jobs: int = 0
