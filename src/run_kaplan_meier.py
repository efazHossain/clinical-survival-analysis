"""
Run Kaplan-Meier survival analysis and log-rank tests.

Outputs:
- reports/figures/km_by_tumor_stage.png
- reports/figures/km_by_er_status.png
- reports/logrank_results.csv
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
from lifelines import KaplanMeierFitter
from lifelines.statistics import multivariate_logrank_test

from config import FIGURES_DIR, PROCESSED_PATH, REPORTS_DIR


def plot_km_by_group(df: pd.DataFrame, group_col: str, output_name: str) -> None:
    kmf = KaplanMeierFitter()

    plt.figure(figsize=(10, 6))

    for group_value, group_df in df.groupby(group_col):
        if pd.isna(group_value) or len(group_df) < 20:
            continue

        kmf.fit(
            durations=group_df["duration_months"],
            event_observed=group_df["event"],
            label=str(group_value),
        )
        kmf.plot_survival_function(ci_show=False)

    plt.title(f"Kaplan-Meier Survival Curves by {group_col}")
    plt.xlabel("Time (Months)")
    plt.ylabel("Survival Probability")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / output_name, dpi=300)
    plt.close()


def run_logrank(df: pd.DataFrame, group_col: str) -> dict[str, float | int | str]:
    subset = df.dropna(subset=[group_col, "duration_months", "event"]).copy()

    result = multivariate_logrank_test(
        event_durations=subset["duration_months"],
        groups=subset[group_col],
        event_observed=subset["event"],
    )

    return {
        "group_variable": group_col,
        "test_statistic": float(result.test_statistic),
        "p_value": float(result.p_value),
        "n": int(len(subset)),
        "n_events": int(subset["event"].sum()),
        "n_groups": int(subset[group_col].nunique()),
    }


def main() -> None:
    if not PROCESSED_PATH.exists():
        raise FileNotFoundError(
            f"Processed file not found: {PROCESSED_PATH}\n"
            "Run: python src/prepare_data.py"
        )

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(PROCESSED_PATH)

    plot_targets = {
        "Tumor Stage": "km_by_tumor_stage.png",
        "ER Status": "km_by_er_status.png",
    }

    results = []

    for group_col, output_name in plot_targets.items():
        if group_col in df.columns:
            print(f"Generating KM plot for {group_col}...")
            plot_km_by_group(df, group_col, output_name)
            results.append(run_logrank(df, group_col))

    results_df = pd.DataFrame(results)
    results_df.to_csv(REPORTS_DIR / "logrank_results.csv", index=False)

    print("Kaplan-Meier analysis complete.")
    print(results_df)
    print(f"Saved figures to: {FIGURES_DIR}")


if __name__ == "__main__":
    main()
