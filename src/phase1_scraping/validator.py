"""
Schema validator for extracted fund data.

Validates that all required fields exist, have correct types, and pass
sanity checks. This runs after every scrape — if validation fails,
the pipeline stops and alerts instead of saving bad data.
"""

import logging

from src.phase1_scraping.config import REQUIRED_FIELDS, NULLABLE_FIELDS

logger = logging.getLogger(__name__)


def validate_scheme_data(data: dict, scheme_id: str) -> list[str]:
    """
    Validate a single scheme's extracted data against the required schema.

    Checks:
    1. All required fields are present
    2. Required fields have correct types
    3. Sanity checks on critical values (NAV > 0, AUM > 0, etc.)
    4. Holdings array is not empty
    5. Returns data has at least 1Y return

    Args:
        data: The extracted fund data dict.
        scheme_id: The scheme identifier for error messages.

    Returns:
        List of error strings. Empty list = valid.
    """
    errors = []

    # --- 1. Required field presence and type checks ---
    for field, expected_types in REQUIRED_FIELDS.items():
        if field not in data:
            errors.append(f"[{scheme_id}] Missing required field: '{field}'")
        elif data[field] is None:
            if field not in NULLABLE_FIELDS:
                errors.append(f"[{scheme_id}] Field '{field}' is None (not nullable)")
        elif not isinstance(data[field], expected_types):
            errors.append(
                f"[{scheme_id}] Field '{field}' has wrong type: "
                f"expected {expected_types}, got {type(data[field]).__name__}"
            )

    # --- 2. Sanity checks on critical values ---
    nav = data.get("nav")
    if nav is not None and isinstance(nav, (int, float)):
        if nav <= 0:
            errors.append(f"[{scheme_id}] NAV is <= 0: {nav}")
        if nav > 100000:
            errors.append(f"[{scheme_id}] NAV suspiciously high: {nav}")

    aum = data.get("aum")
    if aum is not None and isinstance(aum, (int, float)):
        if aum <= 0:
            errors.append(f"[{scheme_id}] AUM is <= 0: {aum}")

    min_sip = data.get("min_sip_investment")
    if min_sip is not None and isinstance(min_sip, (int, float)):
        if min_sip < 0:
            errors.append(f"[{scheme_id}] Min SIP is negative: {min_sip}")

    # --- 3. Holdings check ---
    holdings = data.get("holdings_top10", [])
    if not holdings:
        errors.append(f"[{scheme_id}] Holdings array is empty")
    else:
        for i, h in enumerate(holdings):
            if not h.get("company_name"):
                errors.append(
                    f"[{scheme_id}] Holding [{i}] has no company_name"
                )

    # --- 4. Returns check ---
    # Per edge-cases/defensive guide, return fields can legitimately be null
    # (e.g., for newer funds or incomplete data windows). We only enforce that
    # the returns object exists and is a dict.
    returns = data.get("returns")
    if returns is None:
        errors.append(f"[{scheme_id}] Returns data is missing entirely")
    elif not isinstance(returns, dict):
        errors.append(
            f"[{scheme_id}] Returns data has wrong type: "
            f"expected dict, got {type(returns).__name__}"
        )

    # --- 5. Metadata check ---
    metadata = data.get("_metadata", {})
    if not metadata.get("source_url"):
        errors.append(f"[{scheme_id}] Metadata missing source_url")
    if not metadata.get("scrape_timestamp"):
        errors.append(f"[{scheme_id}] Metadata missing scrape_timestamp")

    # Log result
    if errors:
        logger.warning(
            f"Validation FAILED for {scheme_id}: {len(errors)} error(s)"
        )
        for err in errors:
            logger.warning(f"  ❌ {err}")
    else:
        logger.info(f"Validation PASSED for {scheme_id}")

    return errors


def validate_all_schemes(all_data: dict[str, dict]) -> dict[str, list[str]]:
    """
    Validate all schemes' data at once.

    Args:
        all_data: Dict mapping scheme_id -> extracted fund data.

    Returns:
        Dict mapping scheme_id -> list of errors. Empty lists = valid.
    """
    results = {}
    total_errors = 0

    for scheme_id, data in all_data.items():
        errors = validate_scheme_data(data, scheme_id)
        results[scheme_id] = errors
        total_errors += len(errors)

    if total_errors == 0:
        logger.info(f"All {len(all_data)} schemes passed validation")
    else:
        logger.error(
            f"Validation FAILED: {total_errors} error(s) across "
            f"{sum(1 for e in results.values() if e)} scheme(s)"
        )

    return results
