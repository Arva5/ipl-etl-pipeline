-- Who took the most wickets that are credited to the bowler?

SELECT
    p.player_name,
    COUNT(*) AS wickets
FROM deliveries AS d
JOIN players AS p
    ON d.bowler_id = p.player_id
-- Run outs, retired hurt, and similar dismissals are not the bowler's wicket
WHERE d.dismissal_kind IN (
    'bowled',
    'caught',
    'caught and bowled',
    'lbw',
    'stumped',
    'hit wicket'
)
GROUP BY p.player_id, p.player_name
ORDER BY wickets DESC
LIMIT 10;
