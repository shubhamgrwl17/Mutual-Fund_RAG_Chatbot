# Phase 2 — Data Processing & Section-Based Chunking Implementation Plan

## Goal
Transform the structured JSON files generated in Phase 1 into semantic, text-based chunks optimized for hybrid retrieval and LLM context generation. We will use a "section-based" chunking strategy, mapping specific sets of JSON fields to logical paragraphs (e.g., Returns, Exit Load, Holdings) to prevent context overlap.

## Proposed Changes

### `src/phase2_processing/formatters.py`
Contains null-safe formatting functions for each specific logical chunk. If a value is missing (`None`), it will explicitly state "Not available" rather than omitting the field, ensuring the LLM knows the data is absent rather than hallucinating.
Sections to implement:
- `format_fund_overview`: AMC, launch date, category, description.
- `format_nav_and_aum`: Current NAV, NAV date, AUM.
- `format_expense_ratio`: Expense ratio.
- `format_exit_load`: Exit load string.
- `format_min_investment`: Minimum SIP and lump sum.
- `format_risk_and_benchmark`: Riskometer and benchmark index.
- `format_fund_managers`: Manager names and tenures.
- `format_returns`: 1Y, 3Y, 5Y returns vs Category Average.
- `format_top_holdings`: Formats the top 10 stocks and their allocation percentages.

### `src/phase2_processing/aliases.py`
Maintains a mapping of common scheme aliases (e.g., "hdfc mid cap" -> "hdfc-midcap") which will be injected into chunk metadata to assist the retrieval engine in Phase 4.

### `src/phase2_processing/chunker.py`
The core engine that takes a processed JSON scheme dict, applies the formatters, and yields a list of `Chunk` dictionaries. Each chunk will include:
- `chunk_id` (e.g., `hdfc-midcap_returns`)
- `scheme_id`
- `section`
- `content` (the formatted text)
- `_metadata` (source URL, scrape timestamp, aliases)

### `src/phase2_processing/run_chunking.py`
The pipeline orchestration script. It will:
1. Load all JSON files from `data/processed/`.
2. Pass them through `chunker.py`.
3. Save the resulting chunks to `data/chunks/corpus.jsonl`.

## Verification Plan

### Automated Tests
Run `python -m src.phase2_processing.run_chunking`.

### Manual Verification
1. Inspect `data/chunks/corpus.jsonl`.
2. Verify there are roughly 9-10 chunks per scheme (total ~54-60 chunks).
3. Check `hdfc-midcap_holdings` chunk manually to ensure percentages are formatted correctly (e.g., `Max Financial Services Ltd.: 4.5%`).
4. Check a scheme with known `null` values (like `returns_10y` for newer funds) to ensure the null-safe formatter successfully output "Not available".
