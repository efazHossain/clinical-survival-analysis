"""
Create a consolidated clinical survival modeling summary.

Outputs:
- reports/model_results_summary.md
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from config import REPORTS_DIR


OUTPUT_PATH = REPORTS_DIR / "model_results_summary.md"


def load_csv(path: Path) -> pd.DataFrame | None:
    if path.exists():
        return pd.read_csv(path)
    return None


def add_table(lines: list[str], title: str, df: pd.DataFrame | None) -> None:
    if df is None:
        return

    lines.extend([f"## {title}", "", df.to_markdown(index=False), ""])


def add_rsf_ci_note(lines: list[str], rsf: pd.DataFrame | None) -> None:
    if rsf is None or rsf.empty:
        return

    row = rsf.iloc[0]
    required_cols = [
        "test_c_index_ci_low",
        "test_c_index_ci_high",
        "time_dependent_auc_ci_low",
        "time_dependent_auc_ci_high",
    ]
    if not all(col in rsf.columns for col in required_cols):
        return

    lines.extend(
        [
            "## RSF Bootstrap Confidence Intervals",
            "",
            f"- Test C-index 95% CI: {row['test_c_index_ci_low']:.3f} to {row['test_c_index_ci_high']:.3f}.",
            f"- Mean time-dependent AUC 95% CI: {row['time_dependent_auc_ci_low']:.3f} to {row['time_dependent_auc_ci_high']:.3f}.",
            f"- Bootstrap repeats: {int(row.get('bootstrap_repeats', 0))}; skipped resamples: {int(row.get('bootstrap_skipped', 0))}.",
            "",
        ]
    )


def main() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    data_profile = load_csv(REPORTS_DIR / "data_profile.csv")
    logrank = load_csv(REPORTS_DIR / "logrank_results.csv")
    rsf = load_csv(REPORTS_DIR / "rsf_metrics.csv")
    cox_metrics = load_csv(REPORTS_DIR / "cox_model_metrics.csv")
    cox_stratified_metrics = load_csv(REPORTS_DIR / "cox_stratified_model_metrics.csv")
    cox = load_csv(REPORTS_DIR / "cox_hazard_ratios.csv")
    cox_missingness = load_csv(REPORTS_DIR / "cox_missingness.csv")
    runtime_versions = load_csv(REPORTS_DIR / "runtime_versions.csv")

    lines = [
        "# Clinical Survival Analysis Summary",
        "",
        "## Objective",
        "",
        "Analyze breast cancer patient survival outcomes using Kaplan-Meier curves, log-rank testing, Cox proportional hazards modeling, and Random Survival Forests.",
        "",
    ]

    add_table(lines, "Data Profile", data_profile)
    add_table(lines, "Log-Rank Test Results", logrank)
    add_table(lines, "Cox Model Performance", cox_metrics)
    add_table(lines, "Stratified Cox Sensitivity Performance", cox_stratified_metrics)
    add_table(lines, "Random Survival Forest Performance", rsf)
    add_rsf_ci_note(lines, rsf)

    if cox is not None:
        top_cox = cox.copy()
        if "exp(coef)" in top_cox.columns:
            top_cox["distance_from_1"] = (top_cox["exp(coef)"] - 1).abs()
            top_cox = top_cox.sort_values("distance_from_1", ascending=False).head(10)
            top_cox = top_cox.drop(columns=["distance_from_1"])

        add_table(lines, "Top Cox Model Hazard Ratios", top_cox)

    if cox_missingness is not None:
        add_table(
            lines,
            "Cox Feature Missingness",
            cox_missingness.sort_values("missing_rate", ascending=False).head(12),
        )

    lines.extend(
        [
            "## Diagnostics and Artifacts",
            "",
            "- Cox proportional hazards assumption output: `reports/cox_ph_assumptions.txt`.",
            "- Stratified Cox sensitivity output: `reports/cox_stratified_ph_assumptions.txt`.",
            "- RSF calibration table: `reports/rsf_calibration.csv`.",
            "- Fitted model artifacts are written to `models/` and ignored by Git.",
            "",
            "## Cox Diagnostic Handling",
            "",
            "The baseline Cox assumption check flagged age, ER status, Nottingham prognostic index, and tumor stage. A stratified sensitivity model bins age and Nottingham prognostic index and stratifies by those bins plus ER status and tumor stage. Use the baseline Cox model for coefficient-level interpretation, then compare the stratified sensitivity model before treating those flagged terms as stable proportional hazards.",
            "",
            "## Interpretation",
            "",
            "- Kaplan-Meier curves compare survival probability across clinical groups.",
            "- Log-rank tests evaluate whether survival differences between groups are statistically significant.",
            "- Cox proportional hazards modeling provides interpretable hazard ratios; assumption checks should be reviewed before relying on any coefficient.",
            "- Random Survival Forests capture nonlinear survival patterns and provide model-based risk ranking.",
            "",
            "## Limitations",
            "",
            "- This project is for analytical and educational purposes only.",
            "- Results should not be interpreted as clinical guidance.",
            "- Missing survival status is currently encoded as non-event/censored during preprocessing; review this assumption before clinical interpretation.",
            "- Survival models may be affected by missingness, censoring patterns, cohort bias, and proportional hazards assumptions.",
            "",
        ]
    )

    add_table(lines, "Runtime Versions", runtime_versions)

    OUTPUT_PATH.write_text("\n".join(lines), encoding="utf-8")

    print(f"Saved summary report to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
