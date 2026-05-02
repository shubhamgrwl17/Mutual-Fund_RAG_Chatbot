"""
Data extractor — transforms raw __NEXT_DATA__ into normalized fund data.

Takes the raw mfServerSideData dict from the scraper and extracts/normalizes
specific fields into a clean, consistent schema for downstream processing.
"""

import logging
from datetime import datetime

from src.phase1_scraping.config import FIELD_MAPPING, NESTED_FIELDS

logger = logging.getLogger(__name__)


def extract_flat_fields(mf_data: dict) -> dict:
    """
    Extract simple (non-nested) fields using the FIELD_MAPPING config.

    Args:
        mf_data: The raw mfServerSideData dict.

    Returns:
        Dict with normalized field names and their values.
    """
    result = {}
    for our_key, groww_key in FIELD_MAPPING.items():
        value = mf_data.get(groww_key)
        result[our_key] = value
    return result


def extract_holdings(mf_data: dict, top_n: int = 10) -> list[dict]:
    """
    Extract top N holdings from the fund data.

    Args:
        mf_data: The raw mfServerSideData dict.
        top_n: Number of top holdings to extract (default: 10).

    Returns:
        List of dicts with company_name and allocation_percent.
    """
    raw_holdings = mf_data.get("holdings", [])
    holdings = []

    for h in raw_holdings[:top_n]:
        holdings.append({
            "company_name": h.get("company_name", "Unknown"),
            "allocation_percent": h.get("corpus_per", 0),
            "sector": h.get("sector_name", "Unknown"),
        })

    return holdings


def compute_sector_allocation_from_holdings(holdings_top10: list[dict]) -> list[dict]:
    """
    Compute a simple sector allocation breakdown from the top holdings list.

    Groww's mfServerSideData does not consistently expose a dedicated
    sector-allocation object across schemes, so we derive an approximate
    allocation by grouping top holdings by their sector and summing weights.
    """
    if not holdings_top10:
        return []

    totals: dict[str, float] = {}
    for h in holdings_top10:
        sector = h.get("sector") or "Unknown"
        weight = h.get("allocation_percent") or 0
        try:
            weight_f = float(weight)
        except (TypeError, ValueError):
            weight_f = 0.0
        totals[sector] = totals.get(sector, 0.0) + weight_f

    # Sort descending by allocation
    return [
        {"sector": sector, "allocation_percent": round(pct, 4)}
        for sector, pct in sorted(totals.items(), key=lambda x: x[1], reverse=True)
    ]


def extract_returns(mf_data: dict) -> dict:
    """
    Extract fund returns (CAGR) from stats or return_stats.

    Args:
        mf_data: The raw mfServerSideData dict.

    Returns:
        Dict with return periods as keys and percentage values.
    """
    returns = {
        "returns_1y": None,
        "returns_3y": None,
        "returns_5y": None,
        "returns_10y": None,
        "returns_since_launch": None,
    }

    # Primary source: stats array (contains FUND_RETURN type)
    stats = mf_data.get("stats", [])
    for stat in stats:
        if stat.get("type") == "FUND_RETURN":
            returns["returns_1y"] = stat.get("stat_1y")
            returns["returns_3y"] = stat.get("stat_3y")
            returns["returns_5y"] = stat.get("stat_5y")
            returns["returns_since_launch"] = stat.get("stat_all")
            break

    # Fallback: return_stats array (first item = fund returns)
    if returns["returns_1y"] is None:
        return_stats = mf_data.get("return_stats", [])
        if return_stats:
            rs = return_stats[0]
            returns["returns_1y"] = rs.get("return1y")
            returns["returns_3y"] = rs.get("return3y")
            returns["returns_5y"] = rs.get("return5y")
            returns["returns_10y"] = rs.get("return10y")
            returns["returns_since_launch"] = rs.get("return_since_created")

    return returns


def extract_category_returns(mf_data: dict) -> dict:
    """
    Extract category average returns for comparison context.

    Args:
        mf_data: The raw mfServerSideData dict.

    Returns:
        Dict with category average returns.
    """
    cat_returns = {
        "category_avg_1y": None,
        "category_avg_3y": None,
        "category_avg_5y": None,
    }

    # Primary source: return_stats[0] (contains cat_returnX keys)
    return_stats = mf_data.get("return_stats", [])
    if return_stats:
        rs = return_stats[0]
        cat_returns["category_avg_1y"] = rs.get("cat_return1y")
        cat_returns["category_avg_3y"] = rs.get("cat_return3y")
        cat_returns["category_avg_5y"] = rs.get("cat_return5y")

    # Fallback: stats array (contains CATEGORY_AVG_RETURN type)
    if cat_returns["category_avg_1y"] is None:
        stats = mf_data.get("stats", [])
        for stat in stats:
            if stat.get("type") == "CATEGORY_AVG_RETURN":
                cat_returns["category_avg_1y"] = stat.get("stat_1y")
                cat_returns["category_avg_3y"] = stat.get("stat_3y")
                cat_returns["category_avg_5y"] = stat.get("stat_5y")
                break

    return cat_returns


def extract_fund_managers(mf_data: dict) -> list[dict]:
    """
    Extract fund manager details.

    Args:
        mf_data: The raw mfServerSideData dict.

    Returns:
        List of fund manager dicts with name, start_date, and experience.
    """
    raw_managers = mf_data.get("fund_manager_details", [])
    managers = []

    for m in raw_managers:
        managers.append({
            "name": m.get("person_name", m.get("fund_manager", "Unknown")),
            "start_date": m.get("date_from", m.get("managing_since", None)),
            "qualification": m.get("qualification", m.get("education", None)),
        })

    return managers


def extract_exit_load_details(mf_data: dict) -> dict:
    """
    Extract detailed exit load information.

    Args:
        mf_data: The raw mfServerSideData dict.

    Returns:
        Dict with exit load text and history.
    """
    exit_load_text = mf_data.get("exit_load", "Not available")
    historic = mf_data.get("historic_exit_loads", [])

    history = []
    for h in historic:
        history.append({
            "note": h.get("note", ""),
            "as_on_date": h.get("as_on_date", ""),
        })

    return {
        "exit_load_text": exit_load_text,
        "exit_load_history": history,
    }


def extract_lock_in(mf_data: dict) -> dict:
    """
    Extract lock-in period information.

    Args:
        mf_data: The raw mfServerSideData dict.

    Returns:
        Dict with lock-in years, months, days. All None = open-ended.
    """
    lock_in = mf_data.get("lock_in", {}) or {}
    return {
        "lock_in_years": lock_in.get("years"),
        "lock_in_months": lock_in.get("months"),
        "lock_in_days": lock_in.get("days"),
    }


def extract_fund_data(mf_data: dict, scheme_id: str, source_url: str) -> dict:
    """
    Main extraction function — combines all extractors into a single
    normalized fund data dict.

    This is the primary entry point for the extraction module.

    Args:
        mf_data: The raw mfServerSideData dict from the scraper.
        scheme_id: Our internal scheme identifier (e.g., "hdfc-midcap").
        source_url: The original Groww URL.

    Returns:
        A fully normalized fund data dict ready for validation and storage.
    """
    logger.info(f"Extracting fund data for scheme: {scheme_id}")

    # Extract all flat fields
    data = extract_flat_fields(mf_data)

    # Add nested/complex fields
    data["holdings_top10"] = extract_holdings(mf_data, top_n=10)
    data["sector_allocation"] = compute_sector_allocation_from_holdings(
        data["holdings_top10"]
    )
    data["returns"] = extract_returns(mf_data)
    data["category_returns"] = extract_category_returns(mf_data)
    data["fund_manager_details"] = extract_fund_managers(mf_data)
    data["exit_load_details"] = extract_exit_load_details(mf_data)
    data["lock_in_period"] = extract_lock_in(mf_data)

    # Add metadata
    data["_metadata"] = {
        "scheme_id": scheme_id,
        "source_url": source_url,
        "scrape_timestamp": datetime.utcnow().isoformat() + "Z",
        "data_source": "__NEXT_DATA__",
        "extractor_version": "1.0.0",
    }

    logger.info(
        f"Extracted {len(data)} fields for {data.get('scheme_name', scheme_id)}"
    )

    return data
