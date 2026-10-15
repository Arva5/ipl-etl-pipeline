-- How many matches and runs were there in each IPL season?

-- This answer is about seasons, not players, so it does not join the players table.
SELECT
    CASE
        WHEN m.season = '2007/08' THEN 2008
        WHEN m.season = '2009/10' THEN 2010
        WHEN m.season = '2020/21' THEN 2020
        ELSE CAST(m.season AS INTEGER)
    END AS season_year,
    COUNT(DISTINCT m.match_id) AS matches,
    SUM(d.total_runs) AS total_runs,
    ROUND(
        SUM(d.total_runs) * 1.0 / COUNT(DISTINCT m.match_id),
        2
    ) AS avg_runs_per_match
FROM matches AS m
JOIN deliveries AS d
    ON m.match_id = d.match_id
GROUP BY season_year
ORDER BY season_year;
