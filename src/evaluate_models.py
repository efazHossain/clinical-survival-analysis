"""
Create a consolidated clinical survival modeling summary.

Outputs:
- reports/model_results_summary.md
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT_DIR / "reports"
OUTPUT_PATH = REPORTS_DIR / "model_results_summary.md"


def load_csv(path: Path) -> pd.DataFrame | None:
    if path.exists():
        return pd.read_csv(path)
    return None


def main() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    logrank = load_csv(REPORTS_DIR / "logrank_results.csv")
    rsf = load_csv(REPORTS_DIR / "rsf_metrics.csv")
    cox = load_csv(REPORTS_DIR / "cox_hazard_ratios.csv")

    lines = [
        "# Clinical Survival Analysis Summary",
        "",
        "## Objective",
        "",
        "Analyze breast cancer patient survival outcomes using Kaplan-Meier curves, log-rank testing, Cox proportional hazards modeling, and Random Survival Forests.",
        "",
    ]

    if logrank is not None:
        lines.extend(
            [
                "## Log-Rank Test Results",
                "",
                logrank.to_markdown(index=False),
                "",
            ]
        )

    if rsf is not None:
        lines.extend(
            [
                "## Random Survival Forest Performance",
                "",
                rsf.to_markdown(index=False),
                "",
            ]
        )

    if cox is not None:
        top_cox = cox.copy()
        if "exp(coef)" in top_cox.columns:
            top_cox["distance_from_1"] = (top_cox["exp(coef)"] - 1).abs()
            top_cox = top_cox.sort_values("distance_from_1", ascending=False).head(10)
            top_cox = top_cox.drop(columns=["distance_from_1"])

        lines.extend(
            [
                "## Top Cox Model Hazard Ratios",
                "",
                top_cox.to_markdown(index=False),
                "",
            ]
        )

    lines.extend(
        [
            "## Interpretation",
            "",
            "- Kaplan-Meier curves compare survival probability across clinical groups.",
            "- Log-rank tests evaluate whether survival differences between groups are statistically significant.",
            "- Cox proportional hazards modeling provides interpretable hazard ratios.",
            "- Random Survival Forests capture nonlinear survival patterns and provide model-based risk ranking.",
            "",
            "## Limitations",
            "",
            "- This project is for analytical and educational purposes only.",
            "- Results should not be interpreted as clinical guidance.",
            "- Survival models may be affected by missingness, censoring patterns, cohort bias, and proportional hazards assumptions.",
        ]
    )

    OUTPUT_PATH.write_text("\n".join(lines), encoding="utf-8")

    print(f"Saved summary report to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()