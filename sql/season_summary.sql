-- How many matches and runs were there in each IPL season?

-- This answer is about seasons, not players, so it does not join the players table.
SELECT
    m.season,
    COUNT(DISTINCT m.match_id) AS matches,
    SUM(d.total_runs) AS total_runs,
    ROUND(
        SUM(d.total_runs) * 1.0 / COUNT(DISTINCT m.match_id),
        2
    ) AS avg_runs_per_match
FROM matches AS m
JOIN deliveries AS d
    ON m.match_id = d.match_id
GROUP BY m.season
ORDER BY m.season;
