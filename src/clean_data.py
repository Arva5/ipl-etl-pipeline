import pandas as pd
from pathlib import Path

# Project folders
PROJECT_ROOT = Path(__file__).parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
CLEAN_DIR = PROJECT_ROOT / "data" / "clean"

# Edit this dictionary if you want different team names
TEAM_NAME_MAP = {
    "Delhi Daredevils": "Delhi Capitals",  # old name of the same team
    "Kings XI Punjab": "Punjab Kings",  # old name of the same team
    "Royal Challengers Bangalore": "Royal Challengers Bengaluru",  # city rename
    "Rising Pune Supergiant": "Rising Pune Supergiants",  # spelling difference
}

# Used only when the city cell is empty
VENUE_TO_CITY = {
    "Sharjah Cricket Stadium": "Sharjah",
    "Dubai International Cricket Stadium": "Dubai",
}


def fix_team_names(df, columns):
    """Replace old / alternate team names using TEAM_NAME_MAP."""
    for col in columns:
        df[col] = df[col].replace(TEAM_NAME_MAP)
    return df


def clean_matches(matches):
    """Clean the matches table."""
    rows_before = len(matches)
    missing_before = int(matches.isna().sum().sum())

    # Same team should always have the same spelling
    matches = fix_team_names(
        matches, ["team1", "team2", "toss_winner", "winner"]
    )

    # city: fill from the stadium when the city was left blank
    matches["city"] = matches["city"].fillna(matches["venue"].map(VENUE_TO_CITY))
    matches["city"] = matches["city"].fillna("Unknown")

    # player_of_match: no award when the match had no result
    matches["player_of_match"] = matches["player_of_match"].fillna("Unknown")

    # winner: abandoned matches have no winner
    matches["winner"] = matches["winner"].fillna("No Result")

    # result_margin: ties and no-result matches have no winning margin
    matches["result_margin"] = matches["result_margin"].fillna(0)

    # target_runs / target_overs: match stopped before a target was set
    matches["target_runs"] = matches["target_runs"].fillna(0)
    matches["target_overs"] = matches["target_overs"].fillna(0)

    # method: blank means Duckworth-Lewis was not used
    matches["method"] = matches["method"].fillna("Regular")

    # date should be a real date, not text
    matches["date"] = pd.to_datetime(matches["date"])

    # these columns are whole numbers after filling blanks
    matches["result_margin"] = matches["result_margin"].astype(int)
    matches["target_runs"] = matches["target_runs"].astype(int)
    matches["target_overs"] = matches["target_overs"].astype(int)

    dupes = int(matches.duplicated().sum())
    matches = matches.drop_duplicates()

    missing_after = int(matches.isna().sum().sum())
    missing_fixed = missing_before - missing_after

    return matches, {
        "file": "matches.csv",
        "rows_before": rows_before,
        "rows_after": len(matches),
        "duplicates_removed": dupes,
        "missing_fixed": missing_fixed,
    }


def clean_deliveries(deliveries):
    """Clean the ball-by-ball table."""
    rows_before = len(deliveries)
    missing_before = int(deliveries.isna().sum().sum())

    deliveries = fix_team_names(
        deliveries, ["batting_team", "bowling_team"]
    )

    # extras_type: blank means this ball was not an extra
    deliveries["extras_type"] = deliveries["extras_type"].fillna("none")

    # player_dismissed: blank means nobody got out on this ball
    deliveries["player_dismissed"] = deliveries["player_dismissed"].fillna("none")

    # dismissal_kind: blank means there was no wicket
    deliveries["dismissal_kind"] = deliveries["dismissal_kind"].fillna("none")

    # fielder: blank means no fielder was involved (or it was not a catch / run out)
    deliveries["fielder"] = deliveries["fielder"].fillna("none")

    # keep run and over columns as numbers
    number_cols = [
        "match_id",
        "inning",
        "over",
        "ball",
        "batsman_runs",
        "extra_runs",
        "total_runs",
        "is_wicket",
    ]
    for col in number_cols:
        deliveries[col] = pd.to_numeric(deliveries[col], errors="coerce")

    dupes = int(deliveries.duplicated().sum())
    deliveries = deliveries.drop_duplicates()

    missing_after = int(deliveries.isna().sum().sum())
    missing_fixed = missing_before - missing_after

    return deliveries, {
        "file": "deliveries.csv",
        "rows_before": rows_before,
        "rows_after": len(deliveries),
        "duplicates_removed": dupes,
        "missing_fixed": missing_fixed,
    }


def print_summary(info):
    print(f"{info['file']}:")
    print(f"  rows before cleaning: {info['rows_before']}")
    print(f"  rows after cleaning:  {info['rows_after']}")
    print(f"  duplicates removed:   {info['duplicates_removed']}")
    print(f"  missing values fixed: {info['missing_fixed']}")
    print()


def main():
    matches_path = RAW_DIR / "matches.csv"
    deliveries_path = RAW_DIR / "deliveries.csv"

    if not matches_path.exists() or not deliveries_path.exists():
        print("Put matches.csv and deliveries.csv in data/raw/ first.")
        return

    CLEAN_DIR.mkdir(parents=True, exist_ok=True)

    matches = pd.read_csv(matches_path)
    deliveries = pd.read_csv(deliveries_path)

    matches, matches_info = clean_matches(matches)
    deliveries, deliveries_info = clean_deliveries(deliveries)

    matches.to_csv(CLEAN_DIR / "matches_clean.csv", index=False)
    deliveries.to_csv(CLEAN_DIR / "deliveries_clean.csv", index=False)

    print("Cleaning complete.")
    print()
    print_summary(matches_info)
    print_summary(deliveries_info)
    print("Saved:")
    print("  data/clean/matches_clean.csv")
    print("  data/clean/deliveries_clean.csv")


if __name__ == "__main__":
    main()
