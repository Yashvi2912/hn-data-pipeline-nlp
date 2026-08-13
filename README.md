# Hacker News Data Pipeline with NLP Enrichment

A small end-to-end data pipeline that ingests live data from the Hacker
News public API, cleans and structures it, enriches it with sentiment and
topic tags, and loads it into a properly modeled SQLite database — on an
automated schedule.

## Why this project

Raw data has no value until it's collected, cleaned, and structured — and
if you can automatically extract meaning from it (sentiment, category) as
it flows through, you turn a plumbing pipeline into something that
directly helps a business act faster. This mirrors real use cases like
brand-sentiment monitoring or auto-routing support tickets by topic.

## Architecture

```
ingest.py        -> pulls raw story data from the HN API (no auth needed)
transform.py      -> cleans records, adds sentiment (VADER) + topic tags
load.py           -> upserts clean records into SQLite (schema.sql)
pipeline.py       -> orchestrates ingest -> transform -> load
run_scheduler.py  -> runs pipeline.py automatically every N minutes
analytics_queries.sql -> example SQL queries against the resulting data
```

**Data model** (`schema.sql`): two tables — `authors` (dimension) and
`stories` (fact), linked by `author_id`. This is intentionally normalized
to demonstrate basic dimensional data modeling rather than dumping
everything into one flat table.

## Setup

```bash
pip install -r requirements.txt
```

## Run it once

```bash
python pipeline.py
```

This creates `pipeline.db` in the project folder, populated with the
current top ~50 Hacker News stories, each tagged with a topic
(`tech` / `business` / `science` / `other`) and a sentiment label
(`positive` / `negative` / `neutral`).

## Run it on a schedule (simulating production orchestration)

```bash
python run_scheduler.py --minutes 30
```

Runs the pipeline automatically every 30 minutes (configurable). In a real
production setup this exact call would sit inside an Airflow DAG, a cron
job, or a cloud scheduler trigger — the pipeline logic itself doesn't
change.

## Explore the data

Open `pipeline.db` with any SQLite client, or run the queries in
`analytics_queries.sql`, e.g.:

```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('pipeline.db')
for row in conn.execute(open('analytics_queries.sql').read().split(';')[0]):
    print(row)
"
```

## Design notes worth mentioning in an interview

- **Separation of concerns**: ingest/transform/load are independent
  modules, each testable on its own — standard ETL practice.
- **Idempotent loads**: re-running the pipeline updates existing stories
  (`ON CONFLICT ... DO UPDATE`) instead of creating duplicates.
- **Enrichment is swappable**: `classify_topic()` is a simple keyword
  matcher on purpose — it's a clearly marked seam where a trained
  classifier or embedding-based approach could drop in without touching
  ingest, load, or scheduling.
- **No API key required**: keeps the project runnable by anyone,
  anywhere, with zero setup friction.

## Possible extensions

- Swap SQLite for Postgres and containerize with Docker
- Replace the scheduler loop with an actual Airflow DAG
- Add a small dashboard (Streamlit) on top of `pipeline.db`
- Swap the keyword topic classifier for a trained model or embeddings +
  cosine similarity
