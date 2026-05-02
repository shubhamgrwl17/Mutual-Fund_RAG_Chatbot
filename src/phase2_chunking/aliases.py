"""
Scheme aliases mapping for metadata injection.
Helps the retrieval engine handle fuzzy queries or common acronyms.
"""

# Mapping of scheme_id to a list of common aliases/names users might type
SCHEME_ALIASES = {
    "hdfc-midcap": [
        "hdfc mid cap", 
        "hdfc midcap", 
        "hdfc mid-cap", 
        "hdfc mid cap opportunities"
    ],
    "nippon-india-growth": [
        "nippon india growth", 
        "nippon india midcap", 
        "nippon midcap", 
        "nippon india mid cap"
    ],
    "motilal-oswal-midcap": [
        "motilal oswal midcap", 
        "motilal midcap", 
        "motilal oswal mid cap"
    ],
    "mirae-asset-midcap": [
        "mirae asset midcap", 
        "mirae midcap", 
        "mirae asset mid cap"
    ],
    "icici-prudential-midcap": [
        "icici prudential midcap", 
        "icici midcap", 
        "icici pru midcap", 
        "icici mid cap"
    ],
    "sbi-magnum-midcap": [
        "sbi magnum midcap", 
        "sbi midcap", 
        "sbi mid cap", 
        "sbi magnum mid cap"
    ],
}

def get_aliases(scheme_id: str) -> list[str]:
    """Return the list of aliases for a given scheme_id."""
    return SCHEME_ALIASES.get(scheme_id, [])
