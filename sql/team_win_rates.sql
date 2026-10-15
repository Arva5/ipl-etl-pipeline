-- How often does each team win, ignoring matches with no result?

-- This answer is about teams, not players, so it does not join the players table.
WITH team_matches AS (
    SELECT team1 AS team, winner, result
    FROM matches
    UNION ALL
    SELECT team2 AS team, winner, result
    FROM matches
)

SELECT
    team,
    COUNT(*) AS matches_played,
    SUM(CASE WHEN team = winner THEN 1 ELSE 0 END) AS matches_won,
    ROUND(
        SUM(CASE WHEN team = winner THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
        2
    ) AS win_percentage
FROM team_matches
WHERE result != 'no result'
GROUP BY team
ORDER BY win_percentage DESC, matches_won DESC;
