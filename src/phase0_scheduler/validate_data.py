import os
import sys
import json
import logging
from pathlib import Path

# Add project root to sys.path for absolute imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.phase1_scraping.validator import validate_scheme_data

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("QualityGate")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

def validate_all_data():
    """
    Final Quality Gate before committing data to the repository.
    Performs sanity checks on the entire corpus.
    """
    logger.info("Starting Final Quality Gate validation...")
    
    errors = []
    processed_files = list(PROCESSED_DIR.glob("*.json"))
    
    # 1. Completeness Check: Ensure all 6 mandatory schemes are present
    if len(processed_files) < 6:
        errors.append(f"Completeness Failure: Expected at least 6 schemes, found {len(processed_files)}")

    # 2. Individual Scheme Validation & Empty Data Check
    for json_path in processed_files:
        scheme_id = json_path.stem
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if not data:
                errors.append(f"[{scheme_id}] Empty Data Failure: JSON file is empty")
                continue
                
            # Reuse Phase 1 validator logic
            scheme_errors = validate_scheme_data(data, scheme_id)
            errors.extend(scheme_errors)
            
            # 3. Sanity Check: NAV swing detection (Mocked for now as we don't store history yet)
            # In a real scenario, we would compare with data/raw_previous/ or a DB
            nav = data.get("nav")
            if nav == 0:
                 errors.append(f"[{scheme_id}] NAV Zero Failure: NAV cannot be 0")

        except Exception as e:
            errors.append(f"[{scheme_id}] Parse Failure: {str(e)}")

    # 4. Result Handling
    if errors:
        logger.error("PIPELINE QUALITY GATE FAILED:")
        for err in errors:
            logger.error(f"  - {err}")
        sys.exit(1)
    else:
        logger.info("PIPELINE QUALITY GATE PASSED: All 6 schemes are valid and complete.")
        sys.exit(0)

if __name__ == "__main__":
    validate_all_data()
