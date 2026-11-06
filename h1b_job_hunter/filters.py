"""Filtering rules: title matching, negative exclusions, clearance, geo, comp, and deduplication."""
import re
from typing import Tuple, Optional

from .config import (
    ROLE_INCLUSIONS,
    SENIORITY_EXCLUSIONS,
    FOUNDING_EXCLUSIONS,
    ANCILLARY_EXCLUSIONS,
    DEFENSE_FEDERAL_EXCLUSIONS,
    HEAVY_ML_EXCLUSIONS,
    DEVOPS_EXCLUSIONS,
    MOBILE_EXCLUSIONS,
    NON_US_LOCATIONS,
    CLEARANCE_KEYWORDS,
    SALARY_FLOOR_USD,
    BLOCKED_COMPANIES
)
from .database import DatabaseManager, normalize_company_name
from .registry import is_tier1_tier2
from .models import RawJob, FilterResult


class JobFilterEngine:
    """Evaluates raw job postings against all eligibility, exclusion, and compensation rules."""

    def __init__(self, db: DatabaseManager, allow_existing_companies: bool = False):
        self.db = db
        self.allow_existing_companies = allow_existing_companies

    def evaluate(self, job: RawJob) -> FilterResult:
        """Run all filter checks in order of computational efficiency."""
        
        # 0. Blocked Companies Check (Application quota reached e.g. Cloudflare, Databricks)
        comp_norm = normalize_company_name(job.company)
        for blocked in BLOCKED_COMPANIES:
            if blocked in comp_norm or comp_norm in blocked:
                return FilterResult(
                    job=job,
                    is_passed=False,
                    rejection_reason=f"BLOCKED_COMPANY: Application quota reached for '{job.company}' (~50 applications reached)"
                )

        # 1. Title Inclusion Check (Fastest in-memory check: drops ~90% non-AI roles instantly)
        title_lower = job.title.lower()
        matched_title = None
        for inc in ROLE_INCLUSIONS:
            if inc in title_lower:
                matched_title = inc
                break
        
        if not matched_title:
            return FilterResult(job=job, is_passed=False, rejection_reason=f"TITLE_NOT_INCLUDED: '{job.title}' does not match target roles")

        # 1b. Mobile / Android / iOS Exclusions (Candidate is AI/Full-Stack SWE, not mobile)
        for mob in MOBILE_EXCLUSIONS:
            if re.search(r'\b' + re.escape(mob) + r'\b', title_lower):
                return FilterResult(job=job, is_passed=False, rejection_reason=f"EXCLUDED_MOBILE: Found '{mob}' in title")

        # 2. Cooldown Registry Check (In-memory cache lookup)
        on_cd, cd_reason = self.db.is_company_on_cooldown(job.company)
        if on_cd:
            return FilterResult(job=job, is_passed=False, rejection_reason=f"COOLDOWN: {cd_reason}")

        # 3. Duplicate Application Check (URL level, in-memory cache lookup)
        if self.db.is_link_applied_or_discovered(job.url):
            return FilterResult(job=job, is_passed=False, rejection_reason="DUPLICATE: Link already tracked or discovered")

        # 4. Duplicate Company Check (Company level, in-memory cache lookup)
        if not self.allow_existing_companies and self.db.is_company_applied(job.company):
            return FilterResult(job=job, is_passed=False, rejection_reason=f"DUPLICATE_COMPANY: Candidate already applied to {job.company}")

        # 5. Strict Negative: Seniority & Leveling
        for sen in SENIORITY_EXCLUSIONS:
            # Word boundary matching to avoid false positives (e.g., 'leadership' vs 'lead')
            if re.search(r'\b' + re.escape(sen) + r'\b', title_lower):
                return FilterResult(job=job, is_passed=False, rejection_reason=f"EXCLUDED_SENIORITY: Found '{sen}' in title")

        # 6. Strict Negative: Founding & Early-Stage
        for fnd in FOUNDING_EXCLUSIONS:
            if fnd in title_lower:
                return FilterResult(job=job, is_passed=False, rejection_reason=f"EXCLUDED_FOUNDING: Found '{fnd}' in title")

        # 7. Strict Negative: Non-technical / Ancillary
        # Exception: 'sales engineer' permitted ONLY if 'forward deployed' is present
        if "sales engineer" in title_lower and "forward deployed" not in title_lower:
            return FilterResult(job=job, is_passed=False, rejection_reason="EXCLUDED_ANCILLARY: 'sales engineer' without forward deployed context")

        for anc in ANCILLARY_EXCLUSIONS:
            if re.search(r'\b' + re.escape(anc) + r'\b', title_lower):
                return FilterResult(job=job, is_passed=False, rejection_reason=f"EXCLUDED_ANCILLARY: Found '{anc}' in title")

        # 8. Federal & Defense Division Exclusions
        dept_str = str(job.categories).lower()
        title_and_dept = f"{title_lower} {dept_str}"
        for def_kw in DEFENSE_FEDERAL_EXCLUSIONS:
            if re.search(r'\b' + re.escape(def_kw) + r'\b', title_and_dept):
                return FilterResult(job=job, is_passed=False, rejection_reason=f"EXCLUDED_DEFENSE_FEDERAL: Found '{def_kw}'")

        # 8b. Heavy ML / Robotics / Autonomous Driving / Statistical Modeling Exclusions
        for ml_kw in HEAVY_ML_EXCLUSIONS:
            if re.search(r'\b' + re.escape(ml_kw) + r'\b', title_and_dept):
                return FilterResult(job=job, is_passed=False, rejection_reason=f"EXCLUDED_HEAVY_ML: Found '{ml_kw}' in title/dept")

        for dev in DEVOPS_EXCLUSIONS:
            if re.search(r'\b' + re.escape(dev) + r'\b', title_lower) and "ai" not in title_lower:
                return FilterResult(job=job, is_passed=False, rejection_reason=f"EXCLUDED_DEVOPS: Pure infrastructure role '{dev}'")

        # 9. Geographic Restriction: US-Only
        loc_str = (job.location_raw or "").lower()
        # Also check title for location mentions e.g. "Forward Deployed Engineer - London"
        combined_loc = f"{loc_str} {title_lower}"
        for non_us in NON_US_LOCATIONS:
            if re.search(r'\b' + re.escape(non_us) + r'\b', combined_loc):
                return FilterResult(job=job, is_passed=False, rejection_reason=f"EXCLUDED_LOCATION: Non-US region '{non_us}' detected")

        # 10. Security Clearance & US Citizenship Exclusions
        full_text = f"{title_lower} {loc_str} {job.description_text or ''}".lower()
        for clr in CLEARANCE_KEYWORDS:
            if clr in full_text:
                return FilterResult(job=job, is_passed=False, rejection_reason=f"EXCLUDED_CLEARANCE: Requires '{clr}'")

        # 11. Compensation Threshold
        # Floor: Base >= $150,000 USD
        # If numeric salary stated, lower bound salary_min MUST be >= $150,000
        # Roles with unstated salaries permitted ONLY for Tier 1 / Tier 2 verified sponsors
        salary_passed = False
        if job.salary_min is not None:
            if job.salary_min >= SALARY_FLOOR_USD:
                salary_passed = True
            else:
                return FilterResult(
                    job=job,
                    is_passed=False,
                    rejection_reason=f"BELOW_SALARY_FLOOR: Stated minimum base ${job.salary_min:,.0f} < ${SALARY_FLOOR_USD:,.0f}"
                )
        else:
            # Unstated salary: check if established Tier 1 / Tier 2 sponsor
            if is_tier1_tier2(job.company):
                salary_passed = True
            else:
                return FilterResult(job=job, is_passed=False, rejection_reason="UNSTATED_SALARY: Company is not a verified Tier 1/2 sponsor whose mid-level base reliably exceeds $150k")

        return FilterResult(
            job=job,
            is_passed=True,
            title_matched=matched_title,
            salary_passed=salary_passed,
            geo_passed=True,
            clearance_passed=True,
            dedup_passed=True,
            cooldown_passed=True
        )
