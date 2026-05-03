"""
Orchestrator for Phase 1 Data Collection.

Fetches data from all configured Groww URLs, extracts __NEXT_DATA__,
normalizes fields, validates the schema, and saves to data/raw/ and data/processed/.
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from time import sleep

from src.phase1_scraping.config import (
    PROCESSED_DIR,
    RAW_DIR,
    SOURCE_REGISTRY_PATH,
    SOURCE_URLS,
)
from src.phase1_scraping.extractor import extract_fund_data
from src.phase1_scraping.scraper import scrape_groww_fund, ScraperError
from src.phase1_scraping.validator import validate_scheme_data

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def setup_directories():
    """Ensure output directories exist."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def save_json(data: dict, path: Path):
    """Save a dict to a JSON file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def run_ingestion():
    """Run the full ingestion pipeline for all configured sources."""
    logger.info(f"Starting Phase 1 Ingestion for {len(SOURCE_URLS)} schemes")
    setup_directories()

    success_count = 0
    failure_count = 0
    source_registry = {}

    for scheme_id, config in SOURCE_URLS.items():
        sleep(2)  # Respectful delay to avoid anti-bot triggers
        url = config["url"]
        logger.info(f"\n--- Processing: {scheme_id} ---")

        try:
            # 1. Scrape
            raw_mf_data = scrape_groww_fund(url)

            # Save raw dump
            raw_path = RAW_DIR / f"{scheme_id}.json"
            save_json(raw_mf_data, raw_path)
            logger.info(f"Saved raw data to {raw_path}")

            # 2. Extract & Normalize
            processed_data = extract_fund_data(raw_mf_data, scheme_id, url)

            # 3. Validate
            errors = validate_scheme_data(processed_data, scheme_id)
            if errors:
                logger.error(f"Validation failed for {scheme_id}. Skipping save.")
                for err in errors:
                    logger.error(f"  - {err}")
                failure_count += 1
                continue

            # 4. Save processed data
            processed_path = PROCESSED_DIR / f"{scheme_id}.json"
            save_json(processed_data, processed_path)
            logger.info(f"Saved processed data to {processed_path}")

            # Record success in registry
            source_registry[scheme_id] = {
                "url": url,
                "scheme_name": config["scheme_name"],
                "amc": config["amc"],
                "last_scraped": processed_data["_metadata"]["scrape_timestamp"],
                "status": "success",
            }
            success_count += 1

        except ScraperError as e:
            logger.error(f"Scraping failed for {scheme_id}: {e}")
            failure_count += 1
            source_registry[scheme_id] = {
                "url": url,
                "status": "failed",
                "error": str(e),
                "last_attempt": datetime.utcnow().isoformat() + "Z",
            }
        except Exception as e:
            logger.exception(f"Unexpected error processing {scheme_id}: {e}")
            failure_count += 1
            source_registry[scheme_id] = {
                "url": url,
                "status": "error",
                "error": str(e),
                "last_attempt": datetime.utcnow().isoformat() + "Z",
            }

    # Save source registry
    save_json(source_registry, SOURCE_REGISTRY_PATH)
    logger.info(f"\nSaved source registry to {SOURCE_REGISTRY_PATH}")

    # Summary
    logger.info("\n=== Ingestion Summary ===")
    logger.info(f"Total schemes: {len(SOURCE_URLS)}")
    logger.info(f"Success: {success_count}")
    logger.info(f"Failed: {failure_count}")

    if failure_count > 0:
        logger.warning("Pipeline completed with errors.")
        sys.exit(1)
    else:
        logger.info("Pipeline completed successfully!")
        sys.exit(0)


if __name__ == "__main__":
    run_ingestion()
