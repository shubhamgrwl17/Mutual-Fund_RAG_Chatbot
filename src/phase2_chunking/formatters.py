"""
Null-safe formatters for Mutual Fund chunks.

Each formatter takes the raw scheme dictionary and returns a 
clean, readable string for a specific logical chunk section.
If data is missing, it explicitly states 'Not available' to 
prevent hallucination.
"""

def safe_str(val, suffix="", prefix=""):
    if val is None or val == "":
        return "Not available"
    return f"{prefix}{val}{suffix}"

def format_fund_overview(data: dict) -> str:
    return (
        f"Fund Name: {safe_str(data.get('scheme_name'))}\n"
        f"AMC (Fund House): {safe_str(data.get('fund_house'))}\n"
        f"Category: {safe_str(data.get('category'))} - {safe_str(data.get('sub_category'))}\n"
        f"Launch Date: {safe_str(data.get('launch_date'))}\n"
        f"Description: {safe_str(data.get('description'))}"
    )

def format_nav_and_aum(data: dict) -> str:
    # NAV is often a float, ensure formatting
    nav = data.get('nav')
    nav_str = f"₹{nav:.4f}" if isinstance(nav, (int, float)) else "Not available"
    
    aum = data.get('aum')
    aum_str = f"₹{aum:,.2f} Cr" if isinstance(aum, (int, float)) else "Not available"

    return (
        f"Current NAV: {nav_str} (as of {safe_str(data.get('nav_date'))})\n"
        f"Total AUM (Fund Size): {aum_str}"
    )

def format_expense_ratio(data: dict) -> str:
    return f"Expense Ratio: {safe_str(data.get('expense_ratio'), suffix='%')}"

def format_exit_load(data: dict) -> str:
    exit_load_text = data.get('exit_load_details', {}).get('exit_load_text')
    if exit_load_text:
        exit_load_text = exit_load_text.strip()
    return f"Exit Load Rules: {safe_str(exit_load_text)}"

def format_min_investment(data: dict) -> str:
    min_sip = safe_str(data.get('min_sip_investment'), prefix="₹")
    min_lumpsum = safe_str(data.get('min_investment_amount'), prefix="₹")
    
    return (
        f"Minimum SIP Investment: {min_sip}\n"
        f"Minimum Lumpsum Investment: {min_lumpsum}"
    )

def format_risk_and_benchmark(data: dict) -> str:
    risk = data.get('risk')
    if risk:
        risk = risk.replace(" Riskometer", "").strip()
    return (
        f"Risk Category: {safe_str(risk)}\n"
        f"Benchmark Index: {safe_str(data.get('benchmark_name'))}"
    )

def format_fund_managers(data: dict) -> str:
    managers = data.get('fund_manager_details', [])
    if not managers:
        return "Fund Managers: Not available"
    
    manager_strs = []
    for m in managers:
        name = safe_str(m.get('name'))
        start = safe_str(m.get('start_date'))
        manager_strs.append(f"{name} (managing since {start})")
        
    return "Fund Managers:\n- " + "\n- ".join(manager_strs)

def format_returns(data: dict) -> str:
    returns = data.get('returns', {})
    cat_returns = data.get('category_returns', {})
    
    r1y = safe_str(returns.get('returns_1y'), suffix="%")
    r3y = safe_str(returns.get('returns_3y'), suffix="% CAGR")
    r5y = safe_str(returns.get('returns_5y'), suffix="% CAGR")
    r10y = safe_str(returns.get('returns_10y'), suffix="% CAGR")
    r_since = safe_str(returns.get('returns_since_launch'), suffix="% CAGR")
    
    cr1y = safe_str(cat_returns.get('category_avg_1y'), suffix="%")
    cr3y = safe_str(cat_returns.get('category_avg_3y'), suffix="% CAGR")
    cr5y = safe_str(cat_returns.get('category_avg_5y'), suffix="% CAGR")

    return (
        f"Fund Returns vs Category Average:\n"
        f"- 1 Year: Fund {r1y} | Category {cr1y}\n"
        f"- 3 Year: Fund {r3y} | Category {cr3y}\n"
        f"- 5 Year: Fund {r5y} | Category {cr5y}\n"
        f"- 10 Year: Fund {r10y} | Category Not available\n"
        f"- Since Launch: Fund {r_since}"
    )

def format_top_holdings(data: dict) -> str:
    holdings = data.get('holdings_top10', [])
    if not holdings:
        return "Top Holdings: Not available"
    
    holding_strs = []
    for i, h in enumerate(holdings, 1):
        company = safe_str(h.get('company_name'))
        alloc = safe_str(h.get('allocation_percent'), suffix="%")
        sector = safe_str(h.get('sector'))
        holding_strs.append(f"{i}. {company} ({alloc}) - Sector: {sector}")
        
    return "Top 10 Stock Holdings:\n" + "\n".join(holding_strs)


def format_sector_allocation(data: dict) -> str:
    allocation = data.get("sector_allocation", [])
    if not allocation:
        return "Sector Allocation: Not available"

    lines = []
    for i, item in enumerate(allocation, 1):
        sector = safe_str(item.get("sector"))
        pct = safe_str(item.get("allocation_percent"), suffix="%")
        lines.append(f"{i}. {sector}: {pct}")

    return "Sector Allocation (derived from top holdings):\n" + "\n".join(lines)


def format_lock_in(data: dict) -> str:
    lock_in = data.get("lock_in_period", {}) or {}
    years = lock_in.get("lock_in_years")
    months = lock_in.get("lock_in_months")
    days = lock_in.get("lock_in_days")

    if years is None and months is None and days is None:
        return "Lock-in Period: Not applicable (open-ended scheme)."

    parts = []
    if years is not None:
        parts.append(f"{years} year(s)")
    if months is not None:
        parts.append(f"{months} month(s)")
    if days is not None:
        parts.append(f"{days} day(s)")

    return "Lock-in Period: " + ", ".join(parts) + "."
