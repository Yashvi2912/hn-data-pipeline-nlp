"""
transform.py
------------
Transformation + NLP enrichment layer.

Takes raw story dicts from ingest.py and turns them into clean records
ready for loading, adding two NLP-derived fields along the way:

  - sentiment_label / sentiment_score : via VADER sentiment analysis
  - topic                             : via lightweight keyword classification

This is the "value-add" step that a typical pure-plumbing ETL pipeline
skips, but that mirrors a real use case (e.g. auto-tagging incoming
content by sentiment/category so it can be routed or monitored without
manual review).
"""

import logging
from datetime import datetime, timezone
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

logger = logging.getLogger("pipeline.transform")

_analyzer = SentimentIntensityAnalyzer()

# Lightweight keyword-based topic classifier. Not ML-model-grade, but
# demonstrates the enrichment pattern cheaply and transparently - swap
# this function for a trained classifier / embeddings + cosine similarity
# without touching the rest of the pipeline.
_TOPIC_KEYWORDS = {
    "tech": ["ai", "software", "app", "code", "programming", "startup",
             "github", "python", "javascript", "chip", "cloud", "linux",
             "database", "api", "framework", "algorithm", "browser"],
    "business": ["funding", "raise", "acquired", "ipo", "layoffs", "revenue",
                 "ceo", "market", "valuation", "startup", "investors"],
    "science": ["research", "study", "physics", "nasa", "space", "biology",
                "climate", "quantum", "experiment", "discovery"],
}


def classify_topic(title: str) -> str:
    title_lower = title.lower()
    scores = {topic: 0 for topic in _TOPIC_KEYWORDS}
    for topic, keywords in _TOPIC_KEYWORDS.items():
        for kw in keywords:
            if kw in title_lower:
                scores[topic] += 1
    best_topic = max(scores, key=scores.get)
    return best_topic if scores[best_topic] > 0 else "other"


def classify_sentiment(title: str) -> tuple[str, float]:
    scores = _analyzer.polarity_scores(title)
    compound = scores["compound"]
    if compound >= 0.05:
        label = "positive"
    elif compound <= -0.05:
        label = "negative"
    else:
        label = "neutral"
    return label, compound


def clean_and_enrich(raw_stories: list[dict]) -> list[dict]:
    """Clean raw HN items and attach sentiment + topic enrichment.

    Drops records missing a title (can't enrich or display those
    meaningfully) and de-duplicates by story id.
    """
    seen_ids = set()
    clean_records = []
    now_iso = datetime.now(timezone.utc).isoformat()

    for item in raw_stories:
        story_id = item.get("id")
        title = (item.get("title") or "").strip()

        if not story_id or not title or story_id in seen_ids:
            continue
        seen_ids.add(story_id)

        sentiment_label, sentiment_score = classify_sentiment(title)
        topic = classify_topic(title)

        posted_at = None
        if item.get("time"):
            posted_at = datetime.fromtimestamp(item["time"], tz=timezone.utc).isoformat()

        clean_records.append({
            "story_id": story_id,
            "title": title,
            "url": item.get("url"),
            "author": item.get("by", "unknown"),
            "score": item.get("score", 0),
            "posted_at": posted_at,
            "fetched_at": now_iso,
            "sentiment_label": sentiment_label,
            "sentiment_score": sentiment_score,
            "topic": topic,
        })

    logger.info("Transformed %d clean records from %d raw records",
                len(clean_records), len(raw_stories))
    return clean_records
