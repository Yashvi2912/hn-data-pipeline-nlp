"""
pipeline.py
-----------
Orchestrator: runs the full ETL flow end to end.

    ingest.fetch_raw_stories()   -> raw HN API data
    transform.clean_and_enrich() -> cleaned + sentiment/topic tagged
    load.load_records()          -> written into SQLite

Run directly:  python pipeline.py
Run on a schedule: see run_scheduler.py
"""

import logging
import time

from ingest import fetch_raw_stories
from transform import clean_and_enrich
from load import load_records

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("pipeline")


def run_pipeline(limit: int = 50) -> None:
    start = time.time()
    logger.info("Pipeline run started (limit=%d)", limit)

    raw_stories = fetch_raw_stories(limit=limit)
    clean_records = clean_and_enrich(raw_stories)
    written = load_records(clean_records)

    elapsed = time.time() - start
    logger.info("Pipeline run complete: %d records written in %.2fs", written, elapsed)


if __name__ == "__main__":
    run_pipeline(limit=50)
