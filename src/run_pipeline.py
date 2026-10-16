import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src"
RAW_DIR = PROJECT_ROOT / "data" / "raw"

STEPS = [
    (1, "cleaning the data", "clean_data.py"),
    (2, "creating the database", "create_database.py"),
    (3, "loading the database", "load_database.py"),
    (4, "running the queries", "run_queries.py"),
    (5, "making the charts", "make_charts.py"),
]


def check_raw_files():
    """Stop early if the Kaggle CSVs are missing."""
    needed = ["matches.csv", "deliveries.csv"]
    missing = [name for name in needed if not (RAW_DIR / name).exists()]

    if not missing:
        return True

    print("The pipeline cannot start because a raw data file is missing.")
    print("Download the public IPL dataset from Kaggle, then put these files here:")
    for name in missing:
        print(f"  {RAW_DIR / name}")
    return False


def run_step(step_number, label, script_name):
    """Run one script with the same Python that started this file."""
    print(f"Step {step_number} of 5: {label}")
    print("-" * 40)

    result = subprocess.run(
        [sys.executable, str(SRC_DIR / script_name)],
        cwd=PROJECT_ROOT,
    )

    if result.returncode != 0:
        print()
        print(f"Stopped: step {step_number} of 5 failed ({script_name}).")
        return False

    print()
    return True


def main():
    if not check_raw_files():
        sys.exit(1)

    start = time.perf_counter()

    for step_number, label, script_name in STEPS:
        ok = run_step(step_number, label, script_name)
        if not ok:
            sys.exit(1)

    seconds = time.perf_counter() - start
    print("All 5 steps finished successfully.")
    print(f"Total time: {seconds:.1f} seconds.")


if __name__ == "__main__":
    main()
