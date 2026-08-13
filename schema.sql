-- Schema for the Hacker News data pipeline
-- Two tables: a dimension table for authors, a fact table for stories.
-- This is intentionally normalized to demonstrate basic data modeling.

CREATE TABLE IF NOT EXISTS authors (
    author_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    username        TEXT UNIQUE NOT NULL,
    first_seen_at   TEXT NOT NULL   -- ISO timestamp, first time we saw this author
);

CREATE TABLE IF NOT EXISTS stories (
    story_id        INTEGER PRIMARY KEY,   -- native Hacker News item id
    title           TEXT NOT NULL,
    url             TEXT,
    author_id       INTEGER NOT NULL REFERENCES authors(author_id),
    score           INTEGER DEFAULT 0,
    posted_at       TEXT,          -- ISO timestamp of original post
    fetched_at      TEXT NOT NULL, -- ISO timestamp of when our pipeline pulled it
    sentiment_label TEXT,          -- positive / negative / neutral  (NLP enrichment)
    sentiment_score REAL,          -- compound VADER score, -1 to 1
    topic           TEXT           -- tech / business / science / other (NLP enrichment)
);

CREATE INDEX IF NOT EXISTS idx_stories_topic ON stories(topic);
CREATE INDEX IF NOT EXISTS idx_stories_sentiment ON stories(sentiment_label);
