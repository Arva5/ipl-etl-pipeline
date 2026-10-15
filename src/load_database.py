import sqlite3
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent
CLEAN_DIR = PROJECT_ROOT / "data" / "clean"
DB_PATH = PROJECT_ROOT / "data" / "ipl.db"
BATCH_SIZE = 5000

# These are not real people — we store NULL instead of an id
NOT_A_PLAYER = {"none", "Unknown"}


def to_player_id(name, name_to_id):
    """Return the player id, or None when there is no player."""
    if name is None or pd.isna(name) or name in NOT_A_PLAYER:
        return None
    return name_to_id.get(name)


def empty_tables(conn):
    """Delete old rows so running this script twice does not double the data."""
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.execute("DELETE FROM deliveries")
    cursor.execute("DELETE FROM matches")
    cursor.execute("DELETE FROM players")
    conn.commit()


def collect_player_names(matches, deliveries):
    """Build a sorted list of unique real player names."""
    names = set()

    for col in ["batter", "bowler", "non_striker", "player_dismissed", "fielder"]:
        names.update(deliveries[col].dropna().tolist())

    names.update(matches["player_of_match"].dropna().tolist())

    names = {name for name in names if name not in NOT_A_PLAYER}
    return sorted(names)


def load_players(conn, player_names):
    cursor = conn.cursor()
    rows = [(name,) for name in player_names]
    cursor.executemany(
        "INSERT INTO players (player_name) VALUES (?)",
        rows,
    )
    conn.commit()

    # Read ids back so we can look up names later
    name_to_id = {}
    for player_id, player_name in cursor.execute(
        "SELECT player_id, player_name FROM players"
    ):
        name_to_id[player_name] = player_id
    return name_to_id


def insert_in_batches(cursor, sql, rows):
    """Insert many rows a few thousand at a time."""
    for start in range(0, len(rows), BATCH_SIZE):
        batch = rows[start : start + BATCH_SIZE]
        cursor.executemany(sql, batch)


def load_matches(conn, matches, name_to_id):
    cursor = conn.cursor()
    rows = []
    for r in matches.itertuples(index=False):
        rows.append(
            (
                int(r.id),
                r.season,
                r.city,
                r.date,
                r.match_type,
                to_player_id(r.player_of_match, name_to_id),
                r.venue,
                r.team1,
                r.team2,
                r.toss_winner,
                r.toss_decision,
                r.winner,
                r.result,
                int(r.result_margin),
                int(r.target_runs),
                int(r.target_overs),
                r.super_over,
                r.method,
                r.umpire1,
                r.umpire2,
            )
        )

    insert_in_batches(
        cursor,
        """
        INSERT INTO matches (
            match_id, season, city, date, match_type, player_of_match_id,
            venue, team1, team2, toss_winner, toss_decision, winner,
            result, result_margin, target_runs, target_overs,
            super_over, method, umpire1, umpire2
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    conn.commit()


def load_deliveries(conn, deliveries, name_to_id):
    cursor = conn.cursor()
    rows = []
    for r in deliveries.itertuples(index=False):
        rows.append(
            (
                int(r.match_id),
                int(r.inning),
                r.batting_team,
                r.bowling_team,
                int(r.over),
                int(r.ball),
                to_player_id(r.batter, name_to_id),
                to_player_id(r.bowler, name_to_id),
                to_player_id(r.non_striker, name_to_id),
                int(r.batsman_runs),
                int(r.extra_runs),
                int(r.total_runs),
                r.extras_type,
                int(r.is_wicket),
                to_player_id(r.player_dismissed, name_to_id),
                r.dismissal_kind,
                to_player_id(r.fielder, name_to_id),
            )
        )

    insert_in_batches(
        cursor,
        """
        INSERT INTO deliveries (
            match_id, inning, batting_team, bowling_team, over, ball,
            batter_id, bowler_id, non_striker_id, batsman_runs, extra_runs,
            total_runs, extras_type, is_wicket, player_dismissed_id,
            dismissal_kind, fielder_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    conn.commit()


def count_rows(conn, table_name):
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    return cursor.fetchone()[0]


def run_checks(conn):
    """Make sure every foreign key points to a real row."""
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM deliveries d
        LEFT JOIN matches m ON d.match_id = m.match_id
        WHERE m.match_id IS NULL
        """
    )
    bad_matches = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM deliveries d
        WHERE (d.batter_id IS NOT NULL AND d.batter_id NOT IN (SELECT player_id FROM players))
           OR (d.bowler_id IS NOT NULL AND d.bowler_id NOT IN (SELECT player_id FROM players))
           OR (d.non_striker_id IS NOT NULL AND d.non_striker_id NOT IN (SELECT player_id FROM players))
           OR (d.player_dismissed_id IS NOT NULL AND d.player_dismissed_id NOT IN (SELECT player_id FROM players))
           OR (d.fielder_id IS NOT NULL AND d.fielder_id NOT IN (SELECT player_id FROM players))
        """
    )
    bad_delivery_players = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM matches
        WHERE player_of_match_id IS NOT NULL
          AND player_of_match_id NOT IN (SELECT player_id FROM players)
        """
    )
    bad_match_players = cursor.fetchone()[0]

    print("Checks:")
    if bad_matches == 0:
        print("  every match_id in deliveries exists in matches: OK")
    else:
        print(f"  missing match_id rows: {bad_matches}")

    if bad_delivery_players == 0 and bad_match_players == 0:
        print("  every player id used exists in players: OK")
    else:
        print(f"  bad player ids in deliveries: {bad_delivery_players}")
        print(f"  bad player ids in matches: {bad_match_players}")


def main():
    matches_path = CLEAN_DIR / "matches_clean.csv"
    deliveries_path = CLEAN_DIR / "deliveries_clean.csv"

    if not matches_path.exists() or not deliveries_path.exists():
        print("Run src/clean_data.py first so the cleaned CSV files exist.")
        return

    if not DB_PATH.exists():
        print("Run src/create_database.py first so data/ipl.db exists.")
        return

    matches = pd.read_csv(matches_path)
    deliveries = pd.read_csv(deliveries_path)

    conn = sqlite3.connect(DB_PATH)
    empty_tables(conn)

    player_names = collect_player_names(matches, deliveries)
    name_to_id = load_players(conn, player_names)
    load_matches(conn, matches, name_to_id)
    load_deliveries(conn, deliveries, name_to_id)

    print("Load complete.")
    print()
    print("Cleaned files:")
    print(f"  matches_clean.csv:    {len(matches)} rows")
    print(f"  deliveries_clean.csv: {len(deliveries)} rows")
    print()
    print("Database tables:")
    print(f"  players:    {count_rows(conn, 'players')} rows")
    print(f"  matches:    {count_rows(conn, 'matches')} rows")
    print(f"  deliveries: {count_rows(conn, 'deliveries')} rows")
    print()
    run_checks(conn)

    conn.close()


if __name__ == "__main__":
    main()
