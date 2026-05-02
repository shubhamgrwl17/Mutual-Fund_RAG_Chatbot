# Phase 1 — Data Collection & Corpus Curation

## Overview
This module handles extracting structured fund data from Groww mutual fund pages using the `__NEXT_DATA__` JSON approach.

## How It Works
Groww is built on **Next.js**, which embeds all page data as structured JSON inside a `<script id="__NEXT_DATA__">` tag. We extract this JSON directly — no HTML parsing or headless browser required.

## Key Files

| File | Purpose |
|------|---------|
| `config.py` | Source URLs, scheme aliases, and extraction field mappings |
| `scraper.py` | HTTP fetcher with retry logic + `__NEXT_DATA__` JSON extraction |
| `extractor.py` | Extracts and normalizes specific fund data fields from raw JSON |
| `validator.py` | Schema validation — ensures all required fields exist with correct types |
| `run_ingestion.py` | Entry point — orchestrates the full scrape → extract → validate → save pipeline |

## Output
- `data/raw/<scheme_id>.json` — Raw `__NEXT_DATA__` JSON dumps
- `data/processed/<scheme_id>.json` — Cleaned and normalized fund data
- `data/source_registry.json` — Master list of all 6 URLs with scrape timestamps

## Usage

```bash
# Run full ingestion pipeline
python -m src.phase1_scraping.run_ingestion

# The pipeline will:
# 1. Fetch each Groww URL
# 2. Extract __NEXT_DATA__ JSON
# 3. Parse specific fund fields (NAV, AUM, holdings, etc.)
# 4. Validate against schema
# 5. Save raw + processed JSON to data/
```

## Data Structure (from __NEXT_DATA__)
The key data lives at: `props.pageProps.mfServerSideData`

Key fields extracted:
- `scheme_name`, `fund_house`, `fund_manager`
- `nav`, `nav_date`, `aum`, `expense_ratio`
- `exit_load`, `min_sip_investment`, `min_investment_amount`
- `benchmark_name`, `category`, `sub_category`
- `holdings[]` — top stock allocations
- `stats[]` / `return_stats[]` — 1Y, 3Y, 5Y returns
- `historic_fund_expense[]` — expense ratio history
