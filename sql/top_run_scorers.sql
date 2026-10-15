-- Who scored the most runs in IPL, and how fast did they score?

SELECT
    p.player_name,
    SUM(d.batsman_runs) AS total_runs,
    -- A wide is not a ball the batter has to play
    SUM(CASE WHEN d.extras_type != 'wides' THEN 1 ELSE 0 END) AS balls_faced,
    ROUND(
        SUM(d.batsman_runs) * 100.0
        / SUM(CASE WHEN d.extras_type != 'wides' THEN 1 ELSE 0 END),
        2
    ) AS strike_rate
FROM deliveries AS d
JOIN players AS p
    ON d.batter_id = p.player_id
GROUP BY p.player_id, p.player_name
ORDER BY total_runs DESC
LIMIT 10;
