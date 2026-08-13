-- Example analytics queries you can run against pipeline.db once it has data.
-- Useful to have ready for an interview: shows you can go beyond building
-- the pipeline and actually extract insight from what it produces.

-- 1. Story count and average score by topic
SELECT topic,
       COUNT(*)        AS story_count,
       ROUND(AVG(score), 1) AS avg_score
FROM stories
GROUP BY topic
ORDER BY story_count DESC;

-- 2. Sentiment breakdown by topic
SELECT topic,
       sentiment_label,
       COUNT(*) AS n
FROM stories
GROUP BY topic, sentiment_label
ORDER BY topic, sentiment_label;

-- 3. Most prolific authors (dimension table join)
SELECT a.username,
       COUNT(*)              AS story_count,
       ROUND(AVG(s.score), 1) AS avg_score
FROM stories s
JOIN authors a ON s.author_id = a.author_id
GROUP BY a.username
ORDER BY story_count DESC
LIMIT 10;

-- 4. Top 5 highest-scoring negative-sentiment stories
-- (e.g. simulating "what's generating backlash right now")
SELECT title, score, sentiment_score
FROM stories
WHERE sentiment_label = 'negative'
ORDER BY score DESC
LIMIT 5;

-- 5. Stories fetched in the most recent pipeline run
SELECT title, topic, sentiment_label, fetched_at
FROM stories
WHERE fetched_at = (SELECT MAX(fetched_at) FROM stories)
ORDER BY score DESC;
