"""
load.py
-------
Load layer: writes clean, enriched records into SQLite following the
schema in schema.sql. Handles the author dimension table (insert-if-new)
and upserts stories so re-running the pipeline updates scores instead of
creating duplicates.
"""

import sqlite3
import logging
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger("pipeline.load")

DB_PATH = Path(__file__).parent / "pipeline.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    with open(SCHEMA_PATH) as f:
        conn.executescript(f.read())
    conn.commit()


def get_or_create_author(conn: sqlite3.Connection, username: str) -> int:
    cur = conn.execute("SELECT author_id FROM authors WHERE username = ?", (username,))
    row = cur.fetchone()
    if row:
        return row[0]

    now_iso = datetime.now(timezone.utc).isoformat()
    cur = conn.execute(
        "INSERT INTO authors (username, first_seen_at) VALUES (?, ?)",
        (username, now_iso),
    )
    conn.commit()
    return cur.lastrowid


def load_records(records: list[dict]) -> int:
    """Load clean records into the database. Returns count of rows written."""
    conn = get_connection()
    init_db(conn)

    written = 0
    for r in records:
        author_id = get_or_create_author(conn, r["author"])

        conn.execute("""
            INSERT INTO stories (story_id, title, url, author_id, score,
                                  posted_at, fetched_at, sentiment_label,
                                  sentiment_score, topic)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(story_id) DO UPDATE SET
                score = excluded.score,
                fetched_at = excluded.fetched_at,
                sentiment_label = excluded.sentiment_label,
                sentiment_score = excluded.sentiment_score,
                topic = excluded.topic
        """, (
            r["story_id"], r["title"], r["url"], author_id, r["score"],
            r["posted_at"], r["fetched_at"], r["sentiment_label"],
            r["sentiment_score"], r["topic"],
        ))
        written += 1

    conn.commit()
    conn.close()
    logger.info("Loaded %d records into %s", written, DB_PATH)
    return written
