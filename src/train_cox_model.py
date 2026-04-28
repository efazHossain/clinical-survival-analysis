"""
Train Cox proportional hazards model.

Outputs:
- reports/cox_model_summary.csv
- reports/cox_hazard_ratios.csv
- reports/figures/cox_hazard_ratios.png
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from lifelines import CoxPHFitter


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT_DIR / "data" / "processed" / "metabric_survival_processed.csv"
REPORTS_DIR = ROOT_DIR / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"


COX_FEATURES = [
    "Age at Diagnosis",
    "Neoplasm Histologic Grade",
    "Lymph nodes examined positive",
    "Nottingham prognostic index",
    "Tumor Size",
    "Tumor Stage",
    "Chemotherapy",
    "Hormone Therapy",
    "Radio Therapy",
    "ER Status",
    "HER2 Status",
    "PR Status",
]


def prepare_cox_data(df: pd.DataFrame) -> pd.DataFrame:
    available = [col for col in COX_FEATURES if col in df.columns]
    cox_df = df[["duration_months", "event"] + available].copy()

    for col in cox_df.columns:
        if col not in ["duration_months", "event"]:
            cox_df[col] = cox_df[col].replace(["", "NA", "N/A", "Unknown"], pd.NA)

    categorical_cols = cox_df.select_dtypes(include=["object"]).columns.tolist()
    cox_df = pd.get_dummies(cox_df, columns=categorical_cols, drop_first=True)

    for col in cox_df.columns:
        cox_df[col] = pd.to_numeric(cox_df[col], errors="coerce")

    cox_df = cox_df.dropna()

    return cox_df


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


def main() -> None:
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Processed file not found: {DATA_PATH}\n"
            "Run: python src/prepare_data.py"
        )

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(DATA_PATH)
    cox_df = prepare_cox_data(df)

    cph = CoxPHFitter(penalizer=0.1)
    cph.fit(cox_df, duration_col="duration_months", event_col="event")

    summary = cph.summary.copy()
    summary.to_csv(REPORTS_DIR / "cox_model_summary.csv")

    hazard_ratios = summary[["coef", "exp(coef)", "p", "coef lower 95%", "coef upper 95%"]].copy()
    hazard_ratios.to_csv(REPORTS_DIR / "cox_hazard_ratios.csv")

    plot_top_hazard_ratios(summary)

    print("Cox model training complete.")
    print(f"Rows used: {len(cox_df)}")
    print(f"Concordance index: {cph.concordance_index_:.3f}")
    print(f"Saved summary to: {REPORTS_DIR / 'cox_model_summary.csv'}")
    print(f"Saved hazard ratios to: {REPORTS_DIR / 'cox_hazard_ratios.csv'}")


if __name__ == "__main__":
    main()