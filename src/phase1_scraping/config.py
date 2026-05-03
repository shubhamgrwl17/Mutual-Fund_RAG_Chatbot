"""
Configuration for the Mutual Fund FAQ data ingestion pipeline.

Contains:
- Source URLs (6 Groww mid-cap scheme pages)
- Scheme ID mappings
- Field extraction mappings from __NEXT_DATA__
- Schema validation rules
"""

from pathlib import Path

# ----- Project Paths -----
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
CHUNKS_DIR = DATA_DIR / "chunks"
SOURCE_REGISTRY_PATH = DATA_DIR / "source_registry.json"

# ----- Source URLs -----
# All 6 schemes are Mid-Cap category, Direct Growth plan
SOURCE_URLS = {
    "hdfc-midcap": {
        "url": "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
        "scheme_name": "HDFC Mid-Cap Opportunities Fund – Direct Growth",
        "amc": "HDFC AMC",
    },
    "nippon-india-growth": {
        "url": "https://groww.in/mutual-funds/nippon-india-growth-mid-cap-fund-direct-growth",
        "scheme_name": "Nippon India Growth Fund – Direct Growth",
        "amc": "Nippon India AMC",
    },
    "motilal-oswal-midcap": {
        "url": "https://groww.in/mutual-funds/motilal-oswal-most-focused-midcap-30-fund-direct-growth",
        "scheme_name": "Motilal Oswal Midcap Fund – Direct Growth",
        "amc": "Motilal Oswal AMC",
    },
    "mirae-asset-midcap": {
        "url": "https://groww.in/mutual-funds/mirae-asset-midcap-fund-direct-growth",
        "scheme_name": "Mirae Asset Midcap Fund – Direct Growth",
        "amc": "Mirae Asset AMC",
    },
    "icici-prudential-midcap": {
        "url": "https://groww.in/mutual-funds/icici-prudential-midcap-fund-direct-growth",
        "scheme_name": "ICICI Prudential Midcap Fund – Direct Growth",
        "amc": "ICICI Prudential AMC",
    },
    "sbi-magnum-midcap": {
        "url": "https://groww.in/mutual-funds/sbi-mid-cap-direct-plan-growth",
        "scheme_name": "SBI Magnum Midcap Fund – Direct Growth",
        "amc": "SBI MF",
    },
}

# ----- Scheme Name Aliases (for retrieval matching later) -----
SCHEME_ALIASES = {
    "hdfc-midcap": [
        "hdfc mid cap", "hdfc midcap", "hdfc mid-cap", "hdfc mid cap opportunities"
    ],
    "nippon-india-growth": [
        "nippon india growth", "nippon india", "nippon midcap", "nippon india mid cap"
    ],
    "motilal-oswal-midcap": [
        "motilal oswal midcap", "motilal midcap", "motilal oswal mid cap"
    ],
    "mirae-asset-midcap": [
        "mirae asset midcap", "mirae midcap", "mirae asset mid cap"
    ],
    "icici-prudential-midcap": [
        "icici prudential midcap", "icici midcap", "icici pru midcap", "icici mid cap"
    ],
    "sbi-magnum-midcap": [
        "sbi magnum midcap", "sbi midcap", "sbi mid cap", "sbi magnum mid cap"
    ],
}

# ----- HTTP Request Config -----
REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}
REQUEST_TIMEOUT = 30  # Increased timeout for resilience
MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 5  # Increased backoff to be gentler

# ----- __NEXT_DATA__ Field Mapping -----
# Maps our normalized field names to the path inside mfServerSideData
FIELD_MAPPING = {
    # Basic info
    "fund_name": "fund_name",
    "scheme_name": "scheme_name",
    "fund_house": "fund_house",
    "fund_manager": "fund_manager",
    "launch_date": "launch_date",
    "category": "category",
    "sub_category": "sub_category",
    "plan_type": "plan_type",
    "scheme_type": "scheme_type",
    "isin": "isin",
    "scheme_code": "scheme_code",
    "description": "description",

    # Key metrics
    "nav": "nav",
    "nav_date": "nav_date",
    "aum": "aum",
    "expense_ratio": "expense_ratio",
    "exit_load": "exit_load",

    # Investment limits
    "min_sip_investment": "min_sip_investment",
    "max_sip_investment": "max_sip_investment",
    "min_investment_amount": "min_investment_amount",
    "min_withdrawal": "min_withdrawal",

    # Risk & benchmark
    "benchmark_name": "benchmark_name",
    "risk": "nfo_risk",
    "groww_rating": "groww_rating",

    # Flags
    "sip_allowed": "sip_allowed",
    "lumpsum_allowed": "lumpsum_allowed",

    # Stamp duty
    "stamp_duty": "stamp_duty",
}

# Fields that are nested/arrays and need special extraction
NESTED_FIELDS = [
    "holdings",           # list of dicts with company_name, corpus_per
    "stats",              # list of return stat objects
    "return_stats",       # list of return stat objects (CAGR)
    "fund_manager_details",  # list of fund manager info
    "historic_exit_loads",   # list of exit load history
    "lock_in",            # dict with years, months, days
]

# ----- Schema Validation Rules -----
# (field_name, expected_types, required)
REQUIRED_FIELDS = {
    "fund_name": (str,),
    "scheme_name": (str,),
    "nav": (int, float),
    "aum": (int, float),
    "expense_ratio": (str, int, float),
    "exit_load": (str,),
    "min_sip_investment": (int, float),
    "min_investment_amount": (int, float),
    "benchmark_name": (str,),
    "category": (str,),
    "sub_category": (str,),
    "fund_house": (str,),
    "fund_manager": (str,),
}

# Fields that are allowed to be None (e.g., newer funds without 5Y returns)
NULLABLE_FIELDS = {
    "returns_5y",
    "returns_10y",
    "lock_in",
    "description",
}
