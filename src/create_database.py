import sqlite3
from pathlib import Path

# Database file lives in the data folder
PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "data" / "ipl.db"


def create_tables(conn):
    """Drop old tables (if any) and create three empty tables."""
    cursor = conn.cursor()

    # SQLite only checks foreign keys when this is turned on
    cursor.execute("PRAGMA foreign_keys = ON")

    # Drop in this order: child table first, then parents
    cursor.execute("DROP TABLE IF EXISTS deliveries")
    cursor.execute("DROP TABLE IF EXISTS matches")
    cursor.execute("DROP TABLE IF EXISTS players")

    # One row per unique player
    cursor.execute(
        """
        CREATE TABLE players (
            player_id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL UNIQUE
        )
        """
    )

    # One row per match (match_id comes from the CSV id column)
    cursor.execute(
        """
        CREATE TABLE matches (
            match_id INTEGER PRIMARY KEY,
            season TEXT,
            city TEXT,
            date TEXT,
            match_type TEXT,
            player_of_match_id INTEGER,
            venue TEXT,
            team1 TEXT,
            team2 TEXT,
            toss_winner TEXT,
            toss_decision TEXT,
            winner TEXT,
            result TEXT,
            result_margin INTEGER,
            target_runs INTEGER,
            target_overs INTEGER,
            super_over TEXT,
            method TEXT,
            umpire1 TEXT,
            umpire2 TEXT,
            FOREIGN KEY (player_of_match_id) REFERENCES players (player_id)
        )
        """
    )

    # One row per ball, linked to the match and to the players
    cursor.execute(
        """
        CREATE TABLE deliveries (
            delivery_id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER NOT NULL,
            inning INTEGER,
            batting_team TEXT,
            bowling_team TEXT,
            over INTEGER,
            ball INTEGER,
            batter_id INTEGER,
            bowler_id INTEGER,
            non_striker_id INTEGER,
            batsman_runs INTEGER,
            extra_runs INTEGER,
            total_runs INTEGER,
            extras_type TEXT,
            is_wicket INTEGER,
            player_dismissed_id INTEGER,
            dismissal_kind TEXT,
            fielder_id INTEGER,
            FOREIGN KEY (match_id) REFERENCES matches (match_id),
            FOREIGN KEY (batter_id) REFERENCES players (player_id),
            FOREIGN KEY (bowler_id) REFERENCES players (player_id),
            FOREIGN KEY (non_striker_id) REFERENCES players (player_id),
            FOREIGN KEY (player_dismissed_id) REFERENCES players (player_id),
            FOREIGN KEY (fielder_id) REFERENCES players (player_id)
        )
        """
    )

    conn.commit()


def print_schema(conn):
    """Print each table name and its columns."""
    cursor = conn.cursor()

    print("Tables created:")
    for table_name in ["players", "matches", "deliveries"]:
        print()
        print(f"=== {table_name} ===")
        cursor.execute(f"PRAGMA table_info({table_name})")
        for row in cursor.fetchall():
            col_id, name, col_type, not_null, default, is_pk = row
            pk_text = "  (PRIMARY KEY)" if is_pk else ""
            print(f"  {name}  {col_type}{pk_text}")


def main():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    create_tables(conn)
    print(f"Database file: {DB_PATH}")
    print_schema(conn)
    conn.close()


if __name__ == "__main__":
    main()
