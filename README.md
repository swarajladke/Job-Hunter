# H-1B Autonomous AI Job Discovery & Deduplication Engine (`h1b-job-hunter`)

A production-grade, asynchronous job discovery pipeline and CLI tool designed to autonomously scrape, filter, verify, and export live AI engineering roles matching strict compensation thresholds, H-1B transfer requirements, and deduplication against historical tracking sheets.

---

## Key Features

- **Multi-Source ATS Scraping**:
  - **Greenhouse Public API**: Full content parsing for salary bands and qualifications.
  - **Ashby Public API**: Structured compensation and role metadata extraction.
  - **Lever Public API**: Real-time parsing of posting descriptions and departmental categories.
  - **Workday CXS JSON API**: Direct querying of enterprise career portals without HTML fragility.
  - **Playwright Fallback**: Dynamic JS rendering for protected career portals.

- **Zero 404 Link Guarantee**:
  - Asynchronous verification ensuring every exported URL is an active, direct application link (no generic homepages, zero broken links).

- **Strict Compensation & Eligibility Filtering**:
  - Enforces a minimum base salary floor of **$150,000 USD** (unstated comp permitted only for verified Tier 1/2 sponsors).
  - Drops heavy ML / robotics / perception / statistical ads ranking roles, targeting software engineering, agentic AI, LLM systems, fullstack AI, and forward deployed engineering.
  - Drops senior/staff/director/VP/founding and non-technical/DevOps roles.
  - Drops defense contractor positions requiring security clearances or US citizenship.
  - Strictly filters for US-based positions (in-office, hybrid, or US remote).

- **Deduplication & Cooldown Tracking**:
  - SQLite persistent state (`job_hunter_state.db`) ingesting historical application trackers.
  - Exact URL collision prevention (0 duplicate applications).
  - 60-day company cooldown registry (e.g. OpenAI, Sierra, Capital One).
  - Configurable company capping to prevent single-employer flooding.

- **15-Column Formatted Excel Export**:
  - Exports directly to an openpyxl-formatted spreadsheet (`verified_ai_roles_daily_50.xlsx`) with tailored resume fit justifications and candidate persona matching.

---

## Installation

Clone the repository and install in editable mode:

```bash
git clone https://github.com/swarajladke/Job-Hunter.git
cd Job-Hunter
pip install -e .
```

---

## CLI Usage

### 1. Ingest Historical Trackers
Ingests previous tracking sheets (`Application_Tracker_ALL_Merged_900.xlsx` and `november_tracker.xlsx`) into SQLite:
```bash
h1b-job-hunter ingest
```

### 2. Run Autonomous Discovery & Export
Scrapes target ATS boards, verifies live links, and exports 50 AI engineering roles:
```bash
# Allow new roles at previously applied companies (capped per company)
h1b-job-hunter run -n 50 --allow-existing-companies -o verified_ai_roles_daily_50.xlsx

# Strict mode: Only export roles from 100% unapplied companies
h1b-job-hunter run -n 50 -o verified_ai_roles_daily_50.xlsx
```

### 3. Check State & Metrics
Display total tracked companies, applied links, and cooldowns:
```bash
h1b-job-hunter stats
```

---

## Project Structure

```text
├── h1b_job_hunter/
│   ├── connectors/          # Ashby, Greenhouse, Lever, Workday, Playwright
│   ├── config.py            # Candidate persona, keywords, thresholds
│   ├── database.py          # SQLite state manager & URL normalization
│   ├── evaluator.py         # Resume fit & persona justification generator
│   ├── exporter.py          # 15-column styled Excel exporter
│   ├── filters.py           # Multi-stage eligibility & compensation filters
│   ├── models.py            # Pydantic data schemas & metrics
│   ├── pipeline.py          # End-to-end async orchestrator
│   ├── registry.py          # 130+ verified ATS company mappings
│   ├── verifier.py          # Async HTTP link validator
│   └── cli.py               # Click CLI commands
├── setup.py                 # Package setup configuration
└── README.md
```
