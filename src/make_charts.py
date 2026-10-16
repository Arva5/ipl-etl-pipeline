import matplotlib

# Save images only — do not open a window
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"
CHARTS_DIR = PROJECT_ROOT / "charts"


def save_chart(fig, file_name):
    """Keep labels inside the image and save as PNG."""
    fig.tight_layout()
    fig.savefig(CHARTS_DIR / file_name, dpi=150, bbox_inches="tight")
    plt.close(fig)


def chart_top_run_scorers():
    df = pd.read_csv(OUTPUT_DIR / "top_run_scorers.csv")
    # Smallest first so the biggest bar sits at the top
    df = df.sort_values("total_runs", ascending=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(df["player_name"], df["total_runs"], color="steelblue")
    ax.bar_label(bars, padding=4)
    ax.set_title("Top 10 IPL Run Scorers")
    ax.set_xlabel("Total runs")
    ax.set_ylabel("Player")
    save_chart(fig, "top_run_scorers.png")


def chart_best_bowlers():
    df = pd.read_csv(OUTPUT_DIR / "best_bowlers.csv")
    df = df.sort_values("wickets", ascending=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(df["player_name"], df["wickets"], color="seagreen")
    ax.bar_label(bars, padding=4)
    ax.set_title("Top 10 IPL Wicket Takers")
    ax.set_xlabel("Wickets")
    ax.set_ylabel("Player")
    save_chart(fig, "best_bowlers.png")


def chart_team_win_rates():
    df = pd.read_csv(OUTPUT_DIR / "team_win_rates.csv")
    df = df.sort_values("win_percentage", ascending=True)

    fig, ax = plt.subplots(figsize=(11, 7))
    bars = ax.barh(df["team"], df["win_percentage"], color="darkorange")
    ax.bar_label(bars, fmt="%.2f", padding=4)
    ax.set_title("IPL Team Win Percentage")
    ax.set_xlabel("Win percentage")
    ax.set_ylabel("Team")
    save_chart(fig, "team_win_rates.png")


def chart_season_summary():
    df = pd.read_csv(OUTPUT_DIR / "season_summary.csv")
    df = df.sort_values("season_year")

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df["season_year"], df["avg_runs_per_match"], marker="o", color="purple")

    # Put the number above each point
    for year, avg in zip(df["season_year"], df["avg_runs_per_match"]):
        ax.annotate(
            f"{avg:.1f}",
            (year, avg),
            textcoords="offset points",
            xytext=(0, 8),
            ha="center",
            fontsize=8,
        )

    ax.set_title("Average Runs per Match by Season")
    ax.set_xlabel("Season year")
    ax.set_ylabel("Average runs per match")
    ax.set_xticks(df["season_year"])
    ax.tick_params(axis="x", rotation=45)
    save_chart(fig, "season_summary.png")


def main():
    if not OUTPUT_DIR.exists():
        print("Run src/run_queries.py first so the output CSV files exist.")
        return

    CHARTS_DIR.mkdir(parents=True, exist_ok=True)

    chart_top_run_scorers()
    chart_best_bowlers()
    chart_team_win_rates()
    chart_season_summary()

    print("Charts saved in the charts/ folder:")
    print("  top_run_scorers.png")
    print("  best_bowlers.png")
    print("  team_win_rates.png")
    print("  season_summary.png")


if __name__ == "__main__":
    main()
