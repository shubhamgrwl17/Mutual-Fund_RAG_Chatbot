# Scheme name aliases for fuzzy matching and typo resolution

SCHEME_ALIASES = {
    "hdfc-midcap": [
        "hdfc mid cap", "hdfc midcap", "hdfc mid-cap", "hdfc mid", "hdfc"
    ],
    "nippon-india-growth": [
        "nippon india", "nippon growth", "nippon midcap", "nipon", "nippon"
    ],
    "motilal-oswal-midcap": [
        "motilal oswal midcap", "motilal oswal", "motilal midcap", "motilal"
    ],
    "mirae-asset-midcap": [
        "mirae asset midcap", "mirae midcap", "mirae asset", "mirae"
    ],
    "icici-prudential-midcap": [
        "icici prudential midcap", "icici midcap", "icici prudential", "icici"
    ],
    "sbi-magnum-midcap": [
        "sbi magnum midcap", "sbi midcap", "sbi magnum", "sbi"
    ]
}

KNOWN_FUND_NAMES = []
for aliases in SCHEME_ALIASES.values():
    KNOWN_FUND_NAMES.extend(aliases)

def resolve_fund_name(query: str) -> str | None:
    """Returns the canonical scheme_id if an alias is found in the query, else None."""
    query_lower = query.lower()
    for scheme_id, aliases in SCHEME_ALIASES.items():
        for alias in aliases:
            if alias in query_lower:
                return scheme_id
    return None

def detect_out_of_corpus(query: str) -> bool:
    """Returns True if the user asks about a fund we don't have."""
    query_lower = query.lower()
    fund_keywords = ["fund", "scheme", "mutual fund"]
    mentions_fund = any(kw in query_lower for kw in fund_keywords)
    
    # Allow general mid-cap or aggregate queries
    general_keywords = ["mid cap", "midcap", "all funds", "compare"]
    if any(kw in query_lower for kw in general_keywords):
        return False

    if mentions_fund and resolve_fund_name(query_lower) is None:
        return True
    return False

def needs_clarification(query: str) -> bool:
    """Check if query is too vague (no fund name and short)."""
    if resolve_fund_name(query) is None and len(query.split()) < 5:
        return True
    return False
