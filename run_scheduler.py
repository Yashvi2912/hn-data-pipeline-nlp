"""
run_scheduler.py
-----------------
Runs the pipeline automatically every N minutes, simulating a production
orchestration setup (in a real environment this same run_pipeline() call
would be wrapped in an Airflow DAG, cron job, or cloud scheduler trigger).

Usage:
    python run_scheduler.py            # runs every 30 minutes
    python run_scheduler.py --minutes 10
"""

import argparse
import logging
import time

from pipeline import run_pipeline

logger = logging.getLogger("pipeline.scheduler")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--minutes", type=int, default=30,
                         help="Interval in minutes between pipeline runs")
    parser.add_argument("--limit", type=int, default=50,
                         help="Number of top stories to fetch per run")
    args = parser.parse_args()

    logger.info("Starting scheduler: every %d minutes", args.minutes)
    while True:
        run_pipeline(limit=args.limit)
        logger.info("Sleeping for %d minutes...", args.minutes)
        time.sleep(args.minutes * 60)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    )
    main()
