"""Configuration and rules for the H-1B Job Discovery & Deduplication Engine."""
from pathlib import Path
from typing import List, Set, Dict

# Workspace paths
WORKSPACE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = WORKSPACE_DIR / "job_hunter_state.db"
DEFAULT_TRACKERS = [
    WORKSPACE_DIR / "Application_Tracker_ALL_Merged_900.xlsx",
    WORKSPACE_DIR / "november_tracker.xlsx"
]

# Output schema
EXCEL_COLUMNS: List[str] = [
    "Company",
    "Role",
    "Job Posting Link",
    "POC",
    "Status",
    "Location",
    "Salary",
    "H1B Status",
    "Applied Date",
    "Notes",
    "Role focus",
    "Salary review",
    "Qualification review",
    "Resume fit / why included",
    "Gaps and restrictions"
]

# Compensation Floor
SALARY_FLOOR_USD: float = 150000.0

# Hard Company Exclusions / Application Quota Ceilings
# Companies where the candidate has reached application ceilings (e.g. ~50 applications)
# All future scraping, filtering, and export for these companies is permanently halted.
BLOCKED_COMPANIES: Set[str] = {
    "cloudflare",
    "databricks",
    "decagon",
    "applied intuition"
}

# Initial cooldowns & parameters
INITIAL_COOLDOWNS: Dict[str, int] = {
    "openai": 60,
    "sierra": 60,
    "capital one": 60,
    "cloudflare": 365,
    "databricks": 365,
    "decagon": 365,
    "applied intuition": 365
}
DEFAULT_COOLDOWN_DAYS: int = 60

# Role Inclusions (Title Keywords) - Focused strictly on Software/AI Engineering, Agentic AI, and Full Stack
ROLE_INCLUSIONS: List[str] = [
    # Core AI Engineering & Agentic Roles
    "ai engineer",
    "software developer (ai)",
    "software developer - ai",
    "software developer, ai",
    "software engineer (ai)",
    "software engineer - ai",
    "software engineer, ai",
    "agentic ai developer",
    "agentic ai engineer",
    "agentic",
    "ai developer",
    "software engineer, agents",
    "software engineer - agents",
    "software engineer, agent",
    "software engineer - agent",
    "applied ai engineer",
    "applied ai",
    "llm engineer",
    "generative ai engineer",
    "genai engineer",
    "ai systems engineer",
    "ai platform engineer",
    "ai platform",
    "ai backend engineer",
    "ai infrastructure engineer",
    "ai infra",
    "ai software engineer",
    "ai applications engineer",
    "software engineer - ai applications",
    "software engineer, ai applications",
    "software engineer - generative ai",
    "software engineer, generative ai",
    "software engineer - applied ai",
    "software engineer, applied ai",
    "software engineer (applied ai)",
    "software engineer - ai agents",
    "software engineer, ai agents",
    "software engineer, ai/ml",
    "software engineer - ai/ml",
    "software engineer (ai/ml)",
    "ai/ml software engineer",
    "machine learning software engineer",
    "ai native",
    "ai solutions engineer",
    "solutions engineer, ai",
    "solutions engineer (ai)",
    "ai agent engineer",
    "ai agents engineer",
    "ai integration engineer",
    "inference engineer",
    "inference systems engineer",
    "evals engineer",
    "ai evals engineer",
    "foundations engineer",
    "foundation model engineer",
    "foundation models engineer",
    "ai workflow engineer",
    "ai product engineer",
    "product engineer, ai",
    "product engineer - ai",
    "product engineer (ai)",
    "agents engineer",
    "agent engineer",
    "frontier agents",
    "model routing",
    "enterprise genai",
    "enterprise ai",
    "frontier ai",
    "ai compute",
    "ai infrastructure",
    "ai infra",
    "ai systems",
    "enterprise solutions engineer",
    "solutions engineer - usa",
    "solutions engineer, usa",
    "member of technical staff",
    "technical staff",

    # AI-coupled Backend Roles
    "backend software engineer, ai",
    "backend engineer, ai",
    "backend engineer - ai",
    "backend engineer (ai)",
    "backend engineer, ai/ml",
    "backend software engineer, ai/ml",

    # Full-Stack Engineering (Candidate's Amdocs/Capgemini React/Redux + Java microservices edge)
    "full stack developer (ai)",
    "full stack developer - ai",
    "full stack engineer (ai)",
    "full stack engineer - ai",
    "full stack engineer, ai",
    "full stack software engineer",
    "fullstack software engineer",
    "fullstack engineer",
    "full stack developer",
    "full-stack engineer",
    "full-stack software engineer",
    "full-stack developer",
    "software engineer, full-stack",
    "software engineer - full-stack",
    "software engineer (full-stack)",
    "software engineer, full stack",
    "software engineer - full stack",
    "software engineer (full stack)",
    "software engineer, fullstack",
    "software engineer - fullstack",
    "software engineer (fullstack)",
    "ai full stack engineer",
    "ai fullstack engineer",

    # Forward Deployed Roles (Strictly capped at 5-10 per 50)
    "forward deployed engineer (ai)",
    "forward deployed engineer",
    "forward deployed ai",
    "forward deployed software engineer",
    "forward deployed"
]

# Mobile & Native Platform Exclusions (Rishabh is an AI/Full-Stack engineer, not mobile)
MOBILE_EXCLUSIONS: List[str] = [
    "android",
    "ios",
    "mobile",
    "swift",
    "kotlin",
    "flutter",
    "react native"
]

# Role Exclusions (Strict Negatives)
SENIORITY_EXCLUSIONS: List[str] = [
    "staff",
    "principal",
    "lead",
    "director",
    "vp",
    "vice president",
    "head of",
    "architect",
    "distinguished",
    "fellow",
    "chief",
    "manager",
    "intern",
    "internship",
    "co-op",
    "new grad",
    "grad",
    "campus"
]

FOUNDING_EXCLUSIONS: List[str] = [
    "founding engineer",
    "first engineer",
    "founding ai",
    "co-founder",
    "cofounder",
    "founding member"
]

ANCILLARY_EXCLUSIONS: List[str] = [
    "product manager",
    "data analyst",
    "technical writer",
    "technical writing",
    "scrum master",
    "recruiter",
    "account executive",
    "marketing",
    "human resources",
    "researcher",
    "research scientist",
    "data scientist",
    "quant researcher",
    "developer advocate",
    "developer relations",
    "devrel",
    "evangelist",
    "solutions architect",
    "analyst",
    "operations",
    "demand planning"
    # Note: 'sales engineer' is handled conditionally (unless Forward Deployed)
]

# Heavy ML / Robotics / Classical Modeling Exclusions (Drop pure ML, autonomous driving, science roles)
HEAVY_ML_EXCLUSIONS: List[str] = [
    # Autonomous vehicle / robotics / perception / planning
    "perception",
    "sensor sim",
    "sensor",
    "behavior planning",
    "behavior and planning",
    "behavior & planning",
    "motion planning",
    "prediction & planning",
    "planning & prediction",
    "trajectory",
    "maneuvering",
    "driver refinement",
    "robotics",
    "slam",
    "lidar",
    "radar",
    "point cloud",
    # Ads, pricing, auction, tabular recommendation modeling
    "ads forecasting",
    "ad forecasting",
    "marketplace pricing",
    "pricing algorithm",
    "bidding",
    "ads ml",
    "relevance",
    "recsys",
    "ranking",
    # Pure science & research / academic
    "scientist",
    "applied scientist",
    "ml scientist",
    "machine learning scientist",
    "research scientist",
    "deep learning researcher",
    "phd",
    "university grad",
    "master's university grad",
    "campus"
]

# Federal & Defense Contractor Role Exclusions
DEFENSE_FEDERAL_EXCLUSIONS: List[str] = [
    "mission",
    "federal",
    "government",
    "public sector",
    "defense"
]

# Pure DevOps / Infra exclusion (unless AI / SWE dev)
DEVOPS_EXCLUSIONS: List[str] = [
    "devops engineer",
    "site reliability engineer",
    "sre",
    "cloud infrastructure engineer",
    "it support",
    "sysadmin"
]

# Geographic Restrictions (Must be US based)
NON_US_LOCATIONS: List[str] = [
    "emea", "apac", "latam", "london", "uk", "united kingdom", "canada", "toronto", "vancouver",
    "india", "bengaluru", "bangalore", "gurugram", "hyderabad", "germany", "berlin", "munich",
    "singapore", "australia", "sydney", "melbourne", "france", "paris", "ireland", "dublin",
    "netherlands", "amsterdam", "spain", "madrid", "barcelona", "switzerland", "zurich",
    "israel", "tel aviv", "poland", "warsaw", "brazil", "sao paulo", "mexico", "argentina",
    "japan", "tokyo", "south korea", "seoul", "china", "beijing", "shanghai",
    "sweden", "stockholm", "norway", "oslo", "denmark", "copenhagen", "finland", "helsinki",
    "lithuania", "vilnius", "estonia", "tallinn", "latvia", "riga", "czech", "prague",
    "austria", "vienna", "belgium", "brussels", "italy", "rome", "milan", "portugal", "lisbon",
    "hungary", "budapest", "romania", "bucharest"
]

# Security Clearance Exclusions
CLEARANCE_KEYWORDS: List[str] = [
    "ts/sci",
    "top secret",
    "security clearance",
    "active secret",
    "polygraph",
    "us citizenship required",
    "u.s. citizenship required",
    "must be a us citizen",
    "must be a u.s. citizen",
    "us citizens only",
    "u.s. citizens only",
    "dod clearance",
    "department of defense clearance"
]

# Candidate Persona Context
CANDIDATE_PROFILE = {
    "name": "Rishabh Goyal",
    "experience_years": "5–6 years",
    "education": "M.S. in Computer Science from Stevens Institute of Technology (GPA 3.7, 2023); B.Tech in CS (2020)",
    "visa_status": "Active H-1B in the USA. Requires employer support for an H-1B Change of Employer (Transfer). Does not require initial cap lottery sponsorship.",
    "current_role": {
        "title": "AI Engineer",
        "company": "ACORD Solutions Group",
        "dates": "May 2023–Present",
        "location": "New York / New Jersey",
        "highlights": [
            "Production LLM platforms, multi-provider inference routing, intent-driven agentic AI systems (AWS Bedrock AgentCore, LangGraph, PydanticAI)",
            "Externalized core insurance standards and knowledge bases into reusable Model Context Protocol (MCP) tools",
            "Hardened reliability with custom circuit breakers, prompt caching (20% cost reduction), guardrails, Tenacity retries, dynamic rate limiting, automated evaluation harnesses",
            "Document intelligence pipelines processing ~30,000 pages daily (OpenCV computer vision form analysis + OCR, 94% accuracy, 20% cost reduction)"
        ]
    },
    "prior_experience": [
        {
            "title": "Software Developer",
            "company": "Amdocs",
            "dates": "Feb 2022–Aug 2022",
            "highlights": "React/Redux frontend engineering for AT&T 5G real-time billing; Java backend microservices, Kafka streaming, OpenShift"
        },
        {
            "title": "Software Engineer",
            "company": "Capgemini",
            "dates": "Oct 2020–Jan 2022",
            "highlights": "Production conversational AI for Bayer (20k+ users, 5 chatbots), integrated with enterprise systems (Azure, SharePoint, SuccessFactors)"
        }
    ],
    "core_skills": [
        "Python", "Java", "JavaScript", "React/Redux",
        "LLM Orchestration", "Agentic AI (LangGraph, PydanticAI, Bedrock AgentCore)",
        "Model Context Protocol (MCP)", "RAG Pipelines", "Prompt Caching",
        "AWS Bedrock", "Docker", "Kubernetes", "Kafka", "PostgreSQL",
        "OpenCV", "Document Intelligence", "Tenacity", "Evaluation Harnesses"
    ]
}
