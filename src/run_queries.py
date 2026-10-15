import sqlite3
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "data" / "ipl.db"
SQL_DIR = PROJECT_ROOT / "sql"
OUTPUT_DIR = PROJECT_ROOT / "output"

QUERIES = [
    "top_run_scorers.sql",
    "best_bowlers.sql",
    "team_win_rates.sql",
    "season_summary.sql",
]


def run_one_query(conn, sql_name):
    """Read one .sql file, print the result, and save it as CSV."""
    sql_path = SQL_DIR / sql_name
    sql = sql_path.read_text(encoding="utf-8")

    result = pd.read_sql_query(sql, conn)

    print(f"=== {sql_name} ===")
    print(result.to_string(index=False))
    print()

    csv_name = sql_name.replace(".sql", ".csv")
    result.to_csv(OUTPUT_DIR / csv_name, index=False)


def main():
    if not DB_PATH.exists():
        print("Run the earlier steps first so data/ipl.db exists.")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    for sql_name in QUERIES:
        run_one_query(conn, sql_name)
    conn.close()

    print("Results also saved in the output/ folder.")


if __name__ == "__main__":
    main()
