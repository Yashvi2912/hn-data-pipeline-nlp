"""
ingest.py
---------
Ingestion layer: pulls raw story data from the Hacker News public API
(no API key required: https://github.com/HackerNews/API).

Responsible ONLY for fetching raw data. No cleaning, no enrichment here -
keeping ingestion separate from transformation is a standard ETL practice
that makes the pipeline easier to test and debug.
"""

import requests
import logging

TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"

logger = logging.getLogger("pipeline.ingest")


def fetch_top_story_ids(limit: int = 50) -> list[int]:
    """Fetch the IDs of the current top stories on Hacker News."""
    resp = requests.get(TOP_STORIES_URL, timeout=10)
    resp.raise_for_status()
    ids = resp.json()
    return ids[:limit]


def fetch_item(item_id: int) -> dict | None:
    """Fetch a single story's raw data by its HN item id."""
    resp = requests.get(ITEM_URL.format(item_id), timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return data


def fetch_raw_stories(limit: int = 50) -> list[dict]:
    """Fetch top story IDs, then pull the full record for each one.

    Returns a list of raw dicts as given by the HN API. Items that are
    missing, deleted, or not actual 'story' type are skipped.
    """
    ids = fetch_top_story_ids(limit)
    stories = []
    for item_id in ids:
        try:
            item = fetch_item(item_id)
        except requests.RequestException as e:
            logger.warning("Failed to fetch item %s: %s", item_id, e)
            continue

        if not item or item.get("type") != "story" or item.get("dead") or item.get("deleted"):
            continue

        stories.append(item)

    logger.info("Ingested %d raw stories", len(stories))
    return stories


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    raw = fetch_raw_stories(limit=10)
    for s in raw[:3]:
        print(s.get("title"), "-", s.get("score"))
