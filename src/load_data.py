import pandas as pd
from pathlib import Path

# Project folder (one level above src/)
PROJECT_ROOT = Path(__file__).parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"

FILES = ["matches.csv", "deliveries.csv"]


def load_and_show(file_name):
    """Read one CSV and print a short preview."""
    file_path = RAW_DIR / file_name

    # Stop here if the file is not on disk yet
    if not file_path.exists():
        print(f"Missing file: {file_name}")
        print("Download it from Kaggle (IPL matches / deliveries dataset)")
        print(f"and put it here: {file_path}")
        print()
        return

    df = pd.read_csv(file_path)

    print(f"=== {file_name} ===")
    print("Number of rows:", df.shape[0])
    print("Number of columns:", df.shape[1])
    print("Column names:", list(df.columns))
    print("First 5 rows:")
    print(df.head())
    print()


def main():
    for file_name in FILES:
        load_and_show(file_name)


if __name__ == "__main__":
    main()
