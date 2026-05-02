"""
Core engine that transforms a processed JSON dict into a list of Chunk dicts.
"""

from src.phase2_chunking.formatters import (
    format_fund_overview,
    format_nav_and_aum,
    format_expense_ratio,
    format_exit_load,
    format_min_investment,
    format_risk_and_benchmark,
    format_fund_managers,
    format_returns,
    format_top_holdings,
    format_sector_allocation,
    format_lock_in,
)
from src.phase2_chunking.aliases import get_aliases

def process_scheme_to_chunks(scheme_data: dict) -> list[dict]:
    """
    Takes a single scheme's processed JSON data and generates
    section-based chunks for vector indexing.
    """
    chunks = []
    
    metadata = scheme_data.get("_metadata", {})
    scheme_id = metadata.get("scheme_id", "unknown-scheme")
    scheme_name = scheme_data.get("scheme_name", scheme_id)
    aliases = get_aliases(scheme_id)

    # Base chunk template with shared metadata
    def create_chunk(section_name: str, content_str: str) -> dict:
        return {
            "chunk_id": f"{scheme_id}_{section_name}",
            "scheme_id": scheme_id,
            "scheme_name": scheme_name,
            "section": section_name,
            "content": content_str,
            "_metadata": {
                "source_url": metadata.get("source_url"),
                "scrape_timestamp": metadata.get("scrape_timestamp"),
                "aliases": aliases
            }
        }

    # 1. Fund Overview
    chunks.append(create_chunk("fund_overview", format_fund_overview(scheme_data)))
    
    # 2. NAV & AUM
    chunks.append(create_chunk("nav_and_aum", format_nav_and_aum(scheme_data)))
    
    # 3. Expense Ratio
    chunks.append(create_chunk("expense_ratio", format_expense_ratio(scheme_data)))
    
    # 4. Exit Load
    chunks.append(create_chunk("exit_load", format_exit_load(scheme_data)))
    
    # 5. Minimum Investment
    chunks.append(create_chunk("min_investment", format_min_investment(scheme_data)))
    
    # 6. Risk & Benchmark
    chunks.append(create_chunk("risk_and_benchmark", format_risk_and_benchmark(scheme_data)))
    
    # 7. Fund Managers
    chunks.append(create_chunk("fund_manager", format_fund_managers(scheme_data)))
    
    # 8. Returns
    chunks.append(create_chunk("returns", format_returns(scheme_data)))
    
    # 9. Top Holdings
    chunks.append(create_chunk("top_holdings", format_top_holdings(scheme_data)))

    # 10. Sector Allocation
    chunks.append(create_chunk("sector_allocation", format_sector_allocation(scheme_data)))

    # 11. Lock-in Period
    chunks.append(create_chunk("lock_in", format_lock_in(scheme_data)))

    return chunks
