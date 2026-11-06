"""Target company registry and ATS board configuration."""
from typing import Dict, List, Set, Optional


# Verified Tier 1 and Tier 2 sponsors where market-rate mid-level software/AI salaries reliably exceed $150k
TIER1_TIER2_SPONSORS: Set[str] = {
    # Big Tech & Tier 1
    "apple", "microsoft", "amazon", "aws", "google", "deepmind", "meta", "netflix",
    "nvidia", "micron", "salesforce", "adobe", "oracle", "ibm", "cisco", "intel",
    "qualcomm", "tesla", "linkedin", "uber", "samsung", "sony", "bytedance", "tiktok",
    
    # Tier 2 & Established Sponsors
    "intuit", "palantir", "humana", "bloomberg", "visa", "mastercard", "stripe",
    "databricks", "snowflake", "datadog", "mongodb", "confluent", "elastic", "cloudflare",
    "gitlab", "twilio", "red hat", "nutanix", "netapp", "pure storage", "broadcom",
    "vmware", "teradata", "servicenow", "workday", "atlassian", "autodesk", "synopsys",
    "cadence", "servicetitan", "box", "dropbox", "hubspot", "dbt labs", "hashicorp",
    "figma", "canva", "zendesk", "veeva", "adp", "rippling", "toast", "gartner",
    "palo alto networks", "crowdstrike", "zscaler", "fortinet", "okta", "sentinelone",
    "proofpoint", "rapid7", "tenable", "airbnb", "doordash", "instacart", "lyft",
    "pinterest", "robinhood", "coinbase", "reddit", "ebay", "etsy", "expedia",
    "booking", "zillow", "wayfair", "chewy", "duolingo", "yelp", "paypal", "block",
    "square", "cash app", "affirm", "brex", "plaid", "ramp", "bill", "sofi", "marqeta",
    "applied intuition", "anthropic", "perplexity", "linear", "rubrik", "gusto", "chime", "asana",
    "notion", "supabase", "replit", "deepgram", "dust", "synthesia", "flexport", "fivetran", "launchdarkly", "pagerduty", "discord", "checkr",
    "jpmorgan", "jpmorgan chase", "goldman sachs", "morgan stanley", "citigroup",
    "bank of america", "blackrock", "fidelity", "vanguard", "citadel", "two sigma",
    "jane street", "hudson river trading", "de shaw", "point72", "millennium",
    "travelers", "progressive", "allstate", "liberty mutual", "chubb", "marsh mclennan",
    "aon", "wtw", "guidewire", "duck creek", "ccc intelligent solutions",
    "unitedhealth", "optum", "cvs health", "aetna", "elevance", "cigna", "pfizer",
    "moderna", "regeneron", "genentech", "roche", "walmart", "target", "home depot",
    "general motors", "cruise", "waymo", "ford", "rivian", "aurora", "verizon", "at&t"
}

# Domain Edge Companies: Insurance & InsurTech (Rishabh Goyal's domain edge from ACORD Solutions Group)
INSURANCE_EDGE_COMPANIES: Set[str] = {
    "travelers", "progressive", "liberty mutual", "allstate", "chubb", "the hartford",
    "marsh mclennan", "aon", "wtw", "willis towers watson", "guidewire", "duck creek",
    "ccc intelligent solutions", "evolutioniq", "hippo", "kin", "lemonade", "root",
    "next insurance", "pie insurance", "clearcover", "coalition", "corvus", "cowbell",
    "at-bay", "shift technology", "snapsheet", "tractable", "insurify", "policygenius",
    "verisk", "acord", "prudential", "metlife", "new york life", "guardian", "lincoln financial"
}

# Known ATS registry mappings
# Structure: (ats_type, token_or_slug, company_display_name, category, tier, poc_info)
KNOWN_ATS_BOARDS = [
    # --- ASHBY TARGETS ---
    ("ashby", "ramp", "Ramp", "Fintech / AI", "Tier 2", "Ramp Recruiting Team | recruiting@ramp.com | https://ramp.com/careers"),
    ("ashby", "elevenlabs", "ElevenLabs", "AI Labs / Voice", "Unicorn", "ElevenLabs Talent | hiring@elevenlabs.io | https://elevenlabs.io/careers"),
    ("ashby", "cursor", "Anysphere (Cursor)", "AI Developer Tools", "Unicorn", "Cursor Team | founders@anysphere.co | https://cursor.com"),
    ("ashby", "poolside", "Poolside", "AI Labs", "Unicorn", "Poolside Talent | careers@poolside.ai | https://poolside.ai"),
    ("ashby", "cognition", "Cognition (Devin)", "AI Labs / Coding", "Unicorn", "Cognition Hiring | jobs@cognition-labs.com | https://cognition.ai"),
    ("ashby", "baseten", "Baseten", "AI Infra", "Unicorn", "Baseten Recruiting | talent@baseten.co | https://baseten.co"),
    ("ashby", "modal", "Modal Labs", "Cloud / AI Infra", "Unicorn", "Modal Talent | hiring@modal.com | https://modal.com"),
    ("ashby", "fireworks", "Fireworks AI", "AI Inference Cloud", "Unicorn", "Fireworks Talent | careers@fireworks.ai | https://fireworks.ai"),
    ("ashby", "replicate", "Replicate", "AI Cloud", "Unicorn", "Replicate Team | team@replicate.com | https://replicate.com"),
    ("ashby", "pinecone", "Pinecone", "Vector DB / AI", "Tier 2", "Pinecone Recruiting | careers@pinecone.io | https://pinecone.io"),
    ("ashby", "langchain", "LangChain", "Agent Frameworks", "Unicorn", "Harrison Chase | Co-Founder & CEO, LangChain | careers@langchain.dev | https://langchain.com"),
    ("ashby", "weaviate", "Weaviate", "Vector DB / AI", "Unicorn", "Weaviate Talent | jobs@weaviate.io | https://weaviate.io"),
    ("ashby", "unstructured", "Unstructured", "Document Intelligence / AI", "Unicorn", "Unstructured Talent | jobs@unstructured.io | https://unstructured.io"),
    ("ashby", "lancedb", "LanceDB", "Vector DB / AI", "Unicorn", "LanceDB Team | contact@lancedb.com | https://lancedb.com"),
    ("ashby", "chroma", "Chroma", "AI Embeddings / Vector", "Unicorn", "Chroma Hiring | careers@trychroma.com | https://trychroma.com"),
    ("ashby", "qdrant", "Qdrant", "Vector Search / AI", "Unicorn", "Qdrant HR | careers@qdrant.com | https://qdrant.com"),
    ("ashby", "pave", "Pave", "Fintech / Comp", "Unicorn", "Pave Recruiting | jobs@pave.com | https://pave.com"),
    ("ashby", "vannevarlabs", "Vannevar Labs", "National Security / AI", "Unicorn", "Vannevar Talent | hiring@vannevarlabs.com | https://vannevarlabs.com"),
    ("ashby", "mercator", "Mercator", "Applied AI / Logistics", "Growth", "Megha Malpani | Co-Founder, Mercator | https://linkedin.com/in/megha-malpani"),
    ("ashby", "within.ai", "Within (formerly Klarity)", "Document AI / Agents", "Growth", "Ben Chulaluxsiriboon | Technical Recruiting | https://linkedin.com/in/benchulaluxsiriboon"),
    ("ashby", "fieldguide", "Fieldguide", "AI Platform / Advisory", "Growth", "Hannah Meltzer | Senior Technical Recruiter | https://linkedin.com/in/hannah-meltzer2017"),
    ("ashby", "retellai", "Retell AI", "Voice AI Agents", "Growth", "Retell Hiring | contact@retellai.com | https://retellai.com"),
    ("ashby", "legalos", "LegalOS", "Legal AI", "Growth", "LegalOS Talent | talent@legalos.io | https://legalos.io"),
    ("ashby", "latchbio", "LatchBio", "Biotech AI / Data", "Growth", "LatchBio Hiring | careers@latch.bio | https://latch.bio"),
    ("ashby", "exa", "Exa", "AI Search", "Growth", "Exa Team | hiring@exa.ai | https://exa.ai"),
    ("ashby", "ello", "Ello", "AI Edtech", "Growth", "Ello Talent | hello@ello.com | https://ello.com"),
    ("ashby", "cartesia", "Cartesia", "Voice AI / Multimodal", "Growth", "Cartesia Hiring | jobs@cartesia.ai | https://cartesia.ai"),

    # --- GREENHOUSE TARGETS ---
    ("greenhouse", "scaleai", "Scale AI", "AI Labs / Data", "Tier 2", "Scale AI Recruiting | recruiting@scale.com | https://scale.com"),
    ("ashby", "cohere", "Cohere", "AI Labs / LLMs", "Tier 2", "Cohere Talent | talent@cohere.com | https://cohere.com"),
    ("greenhouse", "figma", "Figma", "Design AI", "Tier 2", "Figma Recruiting | recruiting@figma.com | https://figma.com"),
    # ("greenhouse", "cloudflare", "Cloudflare", "Workers AI / Edge", "Tier 2", "Cloudflare Talent | recruiting@cloudflare.com | https://cloudflare.com"),  # Blocked: quota reached (~50 applications)
    # ("greenhouse", "databricks", "Databricks", "Mosaic AI / Lakehouse", "Tier 1", "Databricks Talent | careers@databricks.com | https://databricks.com"),  # Blocked: quota reached (~50 applications)
    ("greenhouse", "mongodb", "MongoDB", "Vector DB / Data", "Tier 2", "MongoDB Recruiting | recruiting@mongodb.com | https://mongodb.com"),
    ("greenhouse", "elastic", "Elastic", "Search & Retrieval AI", "Tier 2", "Elastic Talent | careers@elastic.co | https://elastic.co"),
    ("greenhouse", "confluent", "Confluent", "Streaming AI / Kafka", "Tier 2", "Confluent Talent | recruiting@confluent.io | https://confluent.io"),
    ("greenhouse", "datadog", "Datadog", "Bits AI / Observability", "Tier 2", "Datadog Recruiting | recruiting@datadoghq.com | https://datadoghq.com"),
    ("greenhouse", "okta", "Okta", "Identity AI", "Tier 2", "Okta Talent | careers@okta.com | https://okta.com"),
    ("greenhouse", "zscaler", "Zscaler", "Cybersecurity AI", "Tier 2", "Zscaler Recruiting | careers@zscaler.com | https://zscaler.com"),
    ("greenhouse", "crowdstrike", "CrowdStrike", "Charlotte AI / Security", "Tier 2", "CrowdStrike Recruiting | careers@crowdstrike.com | https://crowdstrike.com"),
    ("greenhouse", "paloaltonetworks", "Palo Alto Networks", "Precision AI / Cortex", "Tier 2", "PANW Talent | careers@paloaltonetworks.com | https://paloaltonetworks.com"),
    ("greenhouse", "purestorage", "Pure Storage", "AI Storage Infra", "Tier 2", "Pure Storage Talent | recruiting@purestorage.com | https://purestorage.com"),
    ("greenhouse", "nutanix", "Nutanix", "Enterprise AI Infra", "Tier 2", "Nutanix Recruiting | careers@nutanix.com | https://nutanix.com"),
    ("greenhouse", "couchbase", "Couchbase", "Vector Search / DB", "Tier 2", "Couchbase Talent | careers@couchbase.com | https://couchbase.com"),
    ("greenhouse", "runwayml", "Runway", "Generative Video AI", "Unicorn", "Runway Talent | careers@runwayml.com | https://runwayml.com"),
    ("greenhouse", "abridge", "Abridge", "Clinical AI", "Unicorn", "Abridge Talent | recruiting@abridge.com | https://abridge.com"),
    ("greenhouse", "hippocraticai", "Hippocratic AI", "Healthcare Agents", "Unicorn", "Hippocratic Talent | careers@hippocraticai.com | https://hippocraticai.com"),
    ("greenhouse", "writer", "Writer", "Enterprise GenAI", "Unicorn", "Writer Talent | hiring@writer.com | https://writer.com"),
    ("greenhouse", "cresta", "Cresta", "Contact Center AI", "Unicorn", "Cresta Talent | careers@cresta.ai | https://cresta.ai"),
    ("greenhouse", "eightfoldai", "Eightfold AI", "Talent Intelligence AI", "Unicorn", "Eightfold Talent | careers@eightfold.ai | https://eightfold.ai"),
    ("greenhouse", "character", "Character.AI", "Consumer LLMs", "Unicorn", "Character.AI Talent | jobs@character.ai | https://character.ai"),
    ("greenhouse", "anyscale", "Anyscale", "Ray / Distributed AI", "Unicorn", "Anyscale Recruiting | careers@anyscale.com | https://anyscale.com"),
    ("greenhouse", "cerebras", "Cerebras", "AI Chips / Inference", "Unicorn", "Cerebras Talent | careers@cerebras.net | https://cerebras.net"),
    ("greenhouse", "groq", "Groq", "LPU Inference Chips", "Unicorn", "Groq Talent | careers@groq.com | https://groq.com"),
    ("greenhouse", "sambanovasystems", "SambaNova", "Enterprise AI Hardware", "Unicorn", "SambaNova Recruiting | careers@sambanova.ai | https://sambanova.ai"),
    ("greenhouse", "togetherai", "Together AI", "Inference & Cloud", "Unicorn", "Together AI Talent | jobs@together.ai | https://together.ai"),
    ("greenhouse", "glean", "Glean", "Enterprise Search AI", "Unicorn", "Glean Talent | careers@glean.com | https://glean.com"),
    ("ashby", "harvey", "Harvey", "Legal AI", "Unicorn", "Harvey Talent | hiring@harvey.ai | https://harvey.ai"),
    ("greenhouse", "cruise", "Cruise", "Autonomous Vehicles", "Tier 2", "Cruise Talent | careers@getcruise.com | https://getcruise.com"),
    ("greenhouse", "waymo", "Waymo", "Autonomous Driving", "Tier 1", "Waymo Talent | careers@waymo.com | https://waymo.com"),
    ("greenhouse", "aurora", "Aurora", "Autonomous Trucking", "Tier 2", "Aurora Talent | careers@aurora.tech | https://aurora.tech"),
    ("greenhouse", "samsara", "Samsara", "IoT & Vision ML", "Tier 2", "Samsara Recruiting | recruiting@samsara.com | https://samsara.com"),
    ("greenhouse", "affirm", "Affirm", "Fintech AI / Risk", "Tier 2", "Affirm Talent | careers@affirm.com | https://affirm.com"),
    ("greenhouse", "brex", "Brex", "Fintech / Expense AI", "Tier 2", "Brex Talent | careers@brex.com | https://brex.com"),
    ("greenhouse", "plaid", "Plaid", "Fintech / Financial Data", "Tier 2", "Plaid Talent | recruiting@plaid.com | https://plaid.com"),
    ("greenhouse", "robinhood", "Robinhood", "Fintech / Trading ML", "Tier 2", "Robinhood Recruiting | careers@robinhood.com | https://robinhood.com"),
    ("greenhouse", "coinbase", "Coinbase", "Crypto / Risk ML", "Tier 2", "Coinbase Talent | careers@coinbase.com | https://coinbase.com"),
    ("greenhouse", "reddit", "Reddit", "Search / Recommendations", "Tier 2", "Reddit Recruiting | careers@redditinc.com | https://redditinc.com"),
    ("greenhouse", "pinterest", "Pinterest", "Visual Search / GenAI", "Tier 2", "Pinterest Recruiting | careers@pinterest.com | https://pinterest.com"),
    ("greenhouse", "toast", "Toast", "Restaurant SaaS ML", "Tier 2", "Toast Talent | careers@toasttab.com | https://toasttab.com"),
    ("greenhouse", "moveworks", "Moveworks", "Enterprise Conversational AI", "Unicorn", "Moveworks Talent | careers@moveworks.ai | https://moveworks.com"),
    ("greenhouse", "workato", "Workato", "Enterprise Automation AI", "Unicorn", "Workato Talent | careers@workato.com | https://workato.com"),
    ("greenhouse", "stripe", "Stripe", "Payments ML / Radar", "Tier 1", "Stripe Recruiting | recruiting@stripe.com | https://stripe.com"),
    ("greenhouse", "dbtlabs", "dbt Labs", "Analytics / AI Data", "Tier 2", "dbt Labs Talent | jobs@dbtlabs.com | https://getdbt.com"),
    ("greenhouse", "snapsheet", "Snapsheet", "Insurance Tech / Claims AI", "InsurTech", "Snapsheet Recruiting | hr@snapsheet.me | https://snapsheet.com"),
    ("greenhouse", "lemonade", "Lemonade", "AI Insurance", "InsurTech", "Lemonade Talent | jobs@lemonade.com | https://lemonade.com"),
    ("greenhouse", "rootinsurance", "Root Insurance", "InsurTech / Telematics", "InsurTech", "Root Talent | careers@joinroot.com | https://joinroot.com"),
    ("greenhouse", "kininsurance", "Kin Insurance", "InsurTech AI", "InsurTech", "Kin Talent | careers@kin.com | https://kin.com"),
    ("greenhouse", "hippoinsurance", "Hippo Insurance", "InsurTech AI", "InsurTech", "Hippo Talent | careers@hippo.com | https://hippo.com"),
    ("greenhouse", "policygenius", "Policygenius", "InsurTech / Brokerage", "InsurTech", "Policygenius Talent | careers@policygenius.com | https://policygenius.com"),
    ("greenhouse", "insurify", "Insurify", "Insurance Comparison AI", "InsurTech", "Insurify Talent | jobs@insurify.com | https://insurify.com"),
    ("greenhouse", "coalition", "Coalition", "Cyber Insurance / AI", "InsurTech", "Coalition Talent | careers@coalitioninc.com | https://coalitioninc.com"),
    ("greenhouse", "guidewire", "Guidewire", "Core Insurance Software", "InsurTech", "Guidewire Talent | careers@guidewire.com | https://guidewire.com"),

    # --- LEVER TARGETS ---
    ("lever", "palantir", "Palantir", "AIP / Enterprise AI", "Tier 2", "Palantir Recruiting | recruiting@palantir.com | https://palantir.com"),
    ("lever", "spotify", "Spotify", "Music Personalization / ML", "Tier 2", "Spotify HR | jobs@spotify.com | https://spotify.com"),
    ("lever", "coursera", "Coursera", "Edtech / GenAI", "Tier 2", "Coursera Talent | recruiting@coursera.org | https://coursera.org"),
    ("lever", "box", "Box", "Box AI / Enterprise Content", "Tier 2", "Box Recruiting | careers@box.com | https://box.com"),
    ("lever", "yelp", "Yelp", "Search & Reviews ML", "Tier 2", "Yelp Recruiting | careers@yelp.com | https://yelp.com"),
    ("lever", "atlassian", "Atlassian", "Atlassian Intelligence / Rovo", "Tier 2", "Atlassian Talent | careers@atlassian.com | https://atlassian.com"),

    # --- ADDITIONAL UNAPPLIED SPONSORS & LABS ---
    ("greenhouse", "coreweave", "CoreWeave", "AI Labs / Cloud", "Unicorn", "CoreWeave Talent | careers@coreweave.com | https://coreweave.com"),
    ("lever", "veeva", "Veeva Systems", "Enterprise SaaS / Life Sciences", "Tier 2", "Veeva Talent | careers@veeva.com | https://veeva.com"),
    ("greenhouse", "sofi", "SoFi", "Fintech / AI", "Tier 2", "SoFi Talent | careers@sofi.org | https://sofi.com"),
    ("greenhouse", "waymo", "Waymo", "Autonomous Vehicles / AI", "Tier 1", "Waymo Talent | careers@waymo.com | https://waymo.com"),
    ("ashby", "applied", "Applied Intuition", "Autonomous Vehicles / AI", "Unicorn", "Applied Intuition Talent | careers@appliedintuition.com | https://appliedintuition.com"),
    ("ashby", "lemonade", "Lemonade", "InsurTech / AI", "InsurTech", "Lemonade Talent | careers@lemonade.com | https://lemonade.com"),
    ("ashby", "hebbia", "Hebbia", "Enterprise AI Search", "Unicorn", "Hebbia Talent | careers@hebbia.ai | https://hebbia.ai"),
    ("ashby", "tavus", "Tavus", "Generative Video / AI", "Unicorn", "Tavus Talent | careers@tavus.io | https://tavus.io"),
    ("ashby", "decagon", "Decagon", "AI Agents", "Unicorn", "Decagon Talent | careers@decagon.ai | https://decagon.ai"),
    ("ashby", "normai", "Norm AI", "Regulatory AI / Compliance", "Unicorn", "Norm AI Talent | careers@norm.ai | https://norm.ai"),
    ("ashby", "vapi", "Vapi", "Voice AI Agents", "Unicorn", "Vapi Talent | careers@vapi.ai | https://vapi.ai"),
    ("ashby", "suno", "Suno", "AI Audio / Music", "Unicorn", "Suno Talent | careers@suno.ai | https://suno.ai"),
    ("greenhouse", "gitlab", "GitLab", "Duo AI / DevSecOps", "Tier 2", "GitLab Talent | careers@gitlab.com | https://gitlab.com"),
    ("greenhouse", "snap", "Snap Inc", "Computer Vision / AR", "Tier 2", "Snap Talent | careers@snap.com | https://snap.com"),
    ("lever", "twosigma", "Two Sigma", "Quant AI", "Tier 2", "Two Sigma Talent | careers@twosigma.com | https://twosigma.com"),
    ("greenhouse", "flatironhealth", "Flatiron Health", "Healthcare AI", "Tier 2", "Flatiron Talent | careers@flatiron.com | https://flatiron.com"),
    ("greenhouse", "thoughtworks", "Thoughtworks", "AI Consulting / Practice", "Tier 2", "Thoughtworks Talent | careers@thoughtworks.com | https://thoughtworks.com"),
    ("greenhouse", "aqr", "AQR Capital", "Quant Trading / AI", "Tier 2", "AQR Talent | careers@aqr.com | https://aqr.com"),
    ("greenhouse", "anthropic", "Anthropic", "AI Labs / LLMs", "Tier 1", "Anthropic Talent | careers@anthropic.com | https://anthropic.com"),
    ("greenhouse", "airbnb", "Airbnb", "AI Search & Infrastructure", "Tier 1", "Airbnb Recruiting | careers@airbnb.com | https://airbnb.com"),
    ("greenhouse", "instacart", "Instacart", "E-Commerce / AI Search", "Tier 2", "Instacart Talent | careers@instacart.com | https://instacart.com"),
    ("greenhouse", "asana", "Asana", "Work Management / AI", "Tier 2", "Asana Talent | careers@asana.com | https://asana.com"),
    ("greenhouse", "rubrik", "Rubrik", "Cloud Security / AI", "Tier 2", "Rubrik Talent | careers@rubrik.com | https://rubrik.com"),
    ("greenhouse", "gusto", "Gusto", "HR / Fintech AI", "Tier 2", "Gusto Talent | careers@gusto.com | https://gusto.com"),
    ("greenhouse", "chime", "Chime", "Fintech / AI", "Tier 2", "Chime Talent | careers@chime.com | https://chime.com"),
    ("greenhouse", "dropbox", "Dropbox", "Cloud / AI", "Tier 2", "Dropbox Talent | careers@dropbox.com | https://dropbox.com"),
    ("greenhouse", "twilio", "Twilio", "Communications / AI", "Tier 2", "Twilio Talent | careers@twilio.com | https://twilio.com"),
    ("greenhouse", "roblox", "Roblox", "Gaming / AI Infra", "Tier 2", "Roblox Talent | careers@roblox.com | https://roblox.com"),
    ("greenhouse", "klaviyo", "Klaviyo", "Marketing AI / SaaS", "Tier 2", "Klaviyo Talent | careers@klaviyo.com | https://klaviyo.com"),
    ("greenhouse", "braze", "Braze", "Engagement AI / SaaS", "Tier 2", "Braze Talent | careers@braze.com | https://braze.com"),
    ("greenhouse", "carta", "Carta", "Fintech / Equity AI", "Tier 2", "Carta Talent | careers@carta.com | https://carta.com"),
    ("ashby", "notion", "Notion", "Productivity / AI Agents", "Tier 2", "Notion Talent | careers@makenotion.com | https://notion.so"),
    ("ashby", "dust", "Dust", "Enterprise AI Agents", "Unicorn", "Dust Talent | jobs@dust.tt | https://dust.tt"),
    ("ashby", "deepgram", "Deepgram", "Voice AI / Speech LLMs", "Unicorn", "Deepgram Talent | careers@deepgram.com | https://deepgram.com"),
    ("ashby", "supabase", "Supabase", "Open Source AI DB / Vector", "Unicorn", "Supabase Talent | careers@supabase.com | https://supabase.com"),
    ("ashby", "replit", "Replit", "AI Developer Agents", "Unicorn", "Replit Talent | jobs@replit.com | https://replit.com"),
    ("ashby", "synthesia", "Synthesia", "Generative AI Video", "Unicorn", "Synthesia Talent | jobs@synthesia.io | https://synthesia.io"),
    ("ashby", "warp", "Warp", "AI Developer Tools", "Unicorn", "Warp Talent | careers@warp.dev | https://warp.dev"),
    ("ashby", "hex", "Hex", "AI Analytics Workspace", "Unicorn", "Hex Talent | careers@hex.tech | https://hex.tech"),
    ("ashby", "granola", "Granola", "AI Notepad / Meetings", "Unicorn", "Granola Talent | careers@granola.ai | https://granola.ai"),
    ("ashby", "runpod", "RunPod", "Cloud AI Compute", "Unicorn", "RunPod Talent | careers@runpod.io | https://runpod.io"),
    ("ashby", "lightning", "Lightning AI", "AI Studio / LLMs", "Unicorn", "Lightning Talent | careers@lightning.ai | https://lightning.ai"),
    ("greenhouse", "block", "Block", "Fintech / AI", "Tier 1", "Block Recruiting | careers@block.xyz | https://block.xyz"),
    ("greenhouse", "flexport", "Flexport", "Supply Chain / AI", "Tier 2", "Flexport Talent | careers@flexport.com | https://flexport.com"),
    ("greenhouse", "fivetran", "Fivetran", "Data / AI Pipelines", "Tier 2", "Fivetran Talent | careers@fivetran.com | https://fivetran.com"),
    ("greenhouse", "launchdarkly", "LaunchDarkly", "Feature Management / AI", "Tier 2", "LaunchDarkly Talent | careers@launchdarkly.com | https://launchdarkly.com"),
    ("greenhouse", "pagerduty", "PagerDuty", "Incident AI / Operations", "Tier 2", "PagerDuty Talent | careers@pagerduty.com | https://pagerduty.com"),
    ("greenhouse", "checkr", "Checkr", "Trust & Safety / AI", "Tier 2", "Checkr Talent | careers@checkr.com | https://checkr.com"),
    ("greenhouse", "duolingo", "Duolingo", "EdTech / GenAI", "Tier 2", "Duolingo Talent | careers@duolingo.com | https://duolingo.com"),
    ("greenhouse", "discord", "Discord", "Communications / AI", "Tier 2", "Discord Talent | careers@discord.com | https://discord.com"),
    ("ashby", "perplexity", "Perplexity AI", "AI Search & Agents", "Unicorn", "Perplexity Talent | careers@perplexity.ai | https://perplexity.ai"),
    ("ashby", "linear", "Linear", "Developer Tools / AI", "Unicorn", "Linear Talent | careers@linear.app | https://linear.app"),
    ("ashby", "pika", "Pika", "Generative AI", "Unicorn", "Pika Talent | careers@pika.art | https://pika.art"),
    ("greenhouse", "virtu", "Virtu Financial", "Fintech / Trading ML", "Tier 2", "Virtu Talent | careers@virtu.com | https://virtu.com"),
    ("lever", "metlife", "MetLife", "Insurance / AI", "InsurTech", "MetLife Talent | careers@metlife.com | https://metlife.com"),

    # --- WORKDAY TARGETS ---
    ("workday", "adp", "ADP", "Enterprise Software", "Tier 2", "ADP Recruiting | careers@adp.com | https://adp.com", "External"),
    ("workday", "micron", "Micron", "Semiconductors / AI Memory", "Tier 1", "Micron Talent | careers@micron.com | https://micron.com", "External"),
    ("workday", "allstate", "Allstate", "Insurance / AI", "InsurTech", "Allstate Recruiting | careers@allstate.com | https://allstate.com", "External"),
    ("workday", "travelers", "Travelers", "Insurance / Claim AI", "InsurTech", "Travelers Recruiting | careers@travelers.com | https://travelers.com", "External"),
    ("workday", "broadcom", "Broadcom", "AI Infrastructure", "Tier 1", "Broadcom Talent | careers@broadcom.com | https://broadcom.com", "External_Career"),
    ("workday", "visa", "Visa", "Payments / Fraud AI", "Tier 1", "Visa Talent | careers@visa.com | https://visa.com", "External")
]


def is_tier1_tier2(company: str) -> bool:
    """Check if company is Tier 1 or Tier 2 sponsor."""
    if not company:
        return False
    norm = company.strip().lower()
    return any(t in norm or norm in t for t in TIER1_TIER2_SPONSORS)


def is_insurance_edge(company: str) -> bool:
    """Check if company aligns with Rishabh's insurance domain edge."""
    if not company:
        return False
    norm = company.strip().lower()
    return any(ins in norm or norm in ins for ins in INSURANCE_EDGE_COMPANIES)
