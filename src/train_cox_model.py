"""
Train Cox proportional hazards model.

Outputs:
- reports/cox_model_summary.csv
- reports/cox_hazard_ratios.csv
- reports/cox_missingness.csv
- reports/cox_model_metrics.csv
- reports/cox_ph_assumptions.txt
- reports/cox_stratified_model_summary.csv
- reports/cox_stratified_model_metrics.csv
- reports/cox_stratified_ph_assumptions.txt
- reports/figures/cox_hazard_ratios.png
- models/cox_model.joblib
- models/cox_stratified_model.joblib
"""

from __future__ import annotations

import contextlib
import io

import joblib
import matplotlib.pyplot as plt
import pandas as pd
from lifelines import CoxPHFitter

from config import COX_FEATURES, FIGURES_DIR, MODELS_DIR, PROCESSED_PATH, REPORTS_DIR
from preprocessing import available_columns, normalize_missing_values, prepare_cox_data


STRATIFIED_COX_STRATA = [
    "age_group",
    "npi_group",
    "tumor_stage_strata",
    "er_status_strata",
]

STRATIFIED_COX_FEATURES = [
    feature
    for feature in COX_FEATURES
    if feature
    not in {
        "Age at Diagnosis",
        "Nottingham prognostic index",
        "Tumor Stage",
        "ER Status",
    }
]


def plot_top_hazard_ratios(summary_df: pd.DataFrame) -> None:
    plot_df = summary_df.copy()
    plot_df["abs_log_hr"] = plot_df["coef"].abs()
    plot_df = plot_df.sort_values("abs_log_hr", ascending=False).head(15)
    plot_df = plot_df.sort_values("exp(coef)", ascending=True)

    plt.figure(figsize=(10, 7))
    plt.barh(plot_df.index, plot_df["exp(coef)"])
    plt.axvline(1.0, linestyle="--")
    plt.xlabel("Hazard Ratio")
    plt.title("Top Cox Model Hazard Ratios")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "cox_hazard_ratios.png", dpi=300)
    plt.close()


def write_assumption_report(cph: CoxPHFitter, cox_df: pd.DataFrame) -> None:
    report_path = REPORTS_DIR / "cox_ph_assumptions.txt"
    write_assumption_report_to_path(cph, cox_df, report_path)


def write_assumption_report_to_path(cph: CoxPHFitter, cox_df: pd.DataFrame, report_path) -> None:
    output = io.StringIO()

    try:
        with contextlib.redirect_stdout(output):
            cph.check_assumptions(cox_df, p_value_threshold=0.05, show_plots=False)
    except Exception as exc:
        output.write("\n")
        output.write(f"Proportional hazards assumption check failed: {exc}\n")

    report_path.write_text(output.getvalue(), encoding="utf-8")


def _safe_quantile_bins(series: pd.Series, q: int, labels: list[str]) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    if numeric.notna().nunique() < 2:
        return pd.Series(["Missing"] * len(series), index=series.index, dtype="object")

    bins = pd.qcut(numeric, q=q, labels=labels, duplicates="drop")
    return bins.astype("object").fillna("Missing").astype(str)


def prepare_stratified_cox_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare a Cox sensitivity model that stratifies flagged PH-violating terms.

    Age and Nottingham prognostic index are binned into quantile strata. Tumor
    stage and ER status are used as categorical strata. The remaining Cox
    predictors stay in the coefficient table.
    """
    features = available_columns(df, STRATIFIED_COX_FEATURES)
    required = ["duration_months", "event"] + features

    stratified_df = df[required].copy()
    stratified_df = normalize_missing_values(stratified_df, protected_cols=["duration_months", "event"])

    stratified_df["age_group"] = _safe_quantile_bins(
        df.get("Age at Diagnosis", pd.Series(index=df.index, dtype="float64")),
        q=4,
        labels=["Q1 youngest", "Q2", "Q3", "Q4 oldest"],
    )
    stratified_df["npi_group"] = _safe_quantile_bins(
        df.get("Nottingham prognostic index", pd.Series(index=df.index, dtype="float64")),
        q=4,
        labels=["Q1 lowest", "Q2", "Q3", "Q4 highest"],
    )
    stratified_df["tumor_stage_strata"] = (
        df.get("Tumor Stage", pd.Series(index=df.index, dtype="object"))
        .replace(["", "NA", "N/A", "Unknown"], pd.NA)
        .fillna("Missing")
        .astype(str)
    )
    stratified_df["er_status_strata"] = (
        df.get("ER Status", pd.Series(index=df.index, dtype="object"))
        .replace(["", "NA", "N/A", "Unknown"], pd.NA)
        .fillna("Missing")
        .astype(str)
    )

    for col in features:
        numeric = pd.to_numeric(stratified_df[col], errors="coerce")
        if numeric.notna().sum() >= stratified_df[col].notna().sum() * 0.9:
            stratified_df[col] = numeric.fillna(numeric.median())
        else:
            stratified_df[col] = stratified_df[col].fillna("Missing")

    categorical_cols = [
        col
        for col in stratified_df.select_dtypes(include=["object", "category"]).columns
        if col not in STRATIFIED_COX_STRATA
    ]
    stratified_df = pd.get_dummies(stratified_df, columns=categorical_cols, drop_first=True)

    for col in stratified_df.columns:
        if col not in STRATIFIED_COX_STRATA:
            stratified_df[col] = pd.to_numeric(stratified_df[col], errors="coerce")

    stratified_df = stratified_df.dropna(subset=["duration_months", "event"])
    return stratified_df


def train_stratified_sensitivity_model(df: pd.DataFrame) -> None:
    stratified_df = prepare_stratified_cox_data(df)
    cph = CoxPHFitter(penalizer=0.1)
    cph.fit(
        stratified_df,
        duration_col="duration_months",
        event_col="event",
        strata=STRATIFIED_COX_STRATA,
    )

    cph.summary.to_csv(REPORTS_DIR / "cox_stratified_model_summary.csv")
    hazard_ratios = cph.summary[["coef", "exp(coef)", "p", "coef lower 95%", "coef upper 95%"]].copy()
    hazard_ratios.to_csv(REPORTS_DIR / "cox_stratified_hazard_ratios.csv")

    metrics = pd.DataFrame(
        [
            {
                "model": "Stratified Cox sensitivity",
                "concordance_index": cph.concordance_index_,
                "n_rows": len(stratified_df),
                "n_events": int(stratified_df["event"].sum()),
                "n_features": len(
                    [
                        col
                        for col in stratified_df.columns
                        if col not in {"duration_months", "event", *STRATIFIED_COX_STRATA}
                    ]
                ),
                "penalizer": cph.penalizer,
                "strata": "; ".join(STRATIFIED_COX_STRATA),
            }
        ]
    )
    metrics.to_csv(REPORTS_DIR / "cox_stratified_model_metrics.csv", index=False)
    write_assumption_report_to_path(
        cph,
        stratified_df,
        REPORTS_DIR / "cox_stratified_ph_assumptions.txt",
    )
    joblib.dump(cph, MODELS_DIR / "cox_stratified_model.joblib")


def main() -> None:
    if not PROCESSED_PATH.exists():
        raise FileNotFoundError(
            f"Processed file not found: {PROCESSED_PATH}\n"
            "Run: python src/prepare_data.py"
        )

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(PROCESSED_PATH)
    cox_df, missingness = prepare_cox_data(df, COX_FEATURES)
    missingness.to_csv(REPORTS_DIR / "cox_missingness.csv", index=False)

    cph = CoxPHFitter(penalizer=0.1)
    cph.fit(cox_df, duration_col="duration_months", event_col="event")

    summary = cph.summary.copy()
    summary.to_csv(REPORTS_DIR / "cox_model_summary.csv")

    hazard_ratios = summary[["coef", "exp(coef)", "p", "coef lower 95%", "coef upper 95%"]].copy()
    hazard_ratios.to_csv(REPORTS_DIR / "cox_hazard_ratios.csv")

    metrics = pd.DataFrame(
        [
            {
                "model": "Cox proportional hazards",
                "concordance_index": cph.concordance_index_,
                "n_rows": len(cox_df),
                "n_events": int(cox_df["event"].sum()),
                "n_features": len([col for col in cox_df.columns if col not in {"duration_months", "event"}]),
                "penalizer": cph.penalizer,
            }
        ]
    )
    metrics.to_csv(REPORTS_DIR / "cox_model_metrics.csv", index=False)

    plot_top_hazard_ratios(summary)
    write_assumption_report(cph, cox_df)
    joblib.dump(cph, MODELS_DIR / "cox_model.joblib")
    train_stratified_sensitivity_model(df)

    print("Cox model training complete.")
    print(f"Rows used: {len(cox_df)}")
    print(f"Concordance index: {cph.concordance_index_:.3f}")
    print(f"Saved summary to: {REPORTS_DIR / 'cox_model_summary.csv'}")
    print(f"Saved hazard ratios to: {REPORTS_DIR / 'cox_hazard_ratios.csv'}")
    print(f"Saved PH assumption report to: {REPORTS_DIR / 'cox_ph_assumptions.txt'}")
    print(f"Saved model artifact to: {MODELS_DIR / 'cox_model.joblib'}")
    print(f"Saved stratified sensitivity model to: {MODELS_DIR / 'cox_stratified_model.joblib'}")


if __name__ == "__main__":
    main()
