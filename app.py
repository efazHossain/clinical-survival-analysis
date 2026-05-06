"""Streamlit dashboard for clinical survival analysis outputs."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st


ROOT_DIR = Path(__file__).resolve().parent
REPORTS_DIR = ROOT_DIR / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"


st.set_page_config(
    page_title="Clinical Survival Analysis",
    layout="wide",
)


@st.cache_data
def load_csv(path: Path) -> pd.DataFrame | None:
    if not path.exists():
        return None
    return pd.read_csv(path)


def metric_value(df: pd.DataFrame | None, column: str, default: str = "N/A") -> str:
    if df is None or df.empty or column not in df.columns:
        return default
    value = df.iloc[0][column]
    if pd.isna(value):
        return default
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def show_table(title: str, df: pd.DataFrame | None) -> None:
    st.subheader(title)
    if df is None or df.empty:
        st.info("No output found. Run `python src/pipeline.py` to generate this table.")
        return
    st.dataframe(df, use_container_width=True, hide_index=True)


def show_image(title: str, path: Path) -> None:
    st.subheader(title)
    if not path.exists():
        st.info("No figure found. Run `python src/pipeline.py` to generate this image.")
        return
    st.image(str(path), use_container_width=True)


data_profile = load_csv(REPORTS_DIR / "data_profile.csv")
logrank = load_csv(REPORTS_DIR / "logrank_results.csv")
cox_metrics = load_csv(REPORTS_DIR / "cox_model_metrics.csv")
cox_stratified_metrics = load_csv(REPORTS_DIR / "cox_stratified_model_metrics.csv")
cox_hr = load_csv(REPORTS_DIR / "cox_hazard_ratios.csv")
cox_missingness = load_csv(REPORTS_DIR / "cox_missingness.csv")
rsf_metrics = load_csv(REPORTS_DIR / "rsf_metrics.csv")
rsf_importance = load_csv(REPORTS_DIR / "rsf_feature_importance.csv")
rsf_calibration = load_csv(REPORTS_DIR / "rsf_calibration.csv")


st.title("Clinical Survival Analysis")

metric_cols = st.columns(5)
metric_cols[0].metric("Processed Rows", metric_value(data_profile, "processed_rows"))
metric_cols[1].metric("Event Rate", metric_value(data_profile, "event_rate"))
metric_cols[2].metric("Cox C-index", metric_value(cox_metrics, "concordance_index"))
metric_cols[3].metric("RSF Test C-index", metric_value(rsf_metrics, "test_c_index"))
metric_cols[4].metric("RSF AUC", metric_value(rsf_metrics, "time_dependent_auc_mean"))

tabs = st.tabs(["Survival", "Cox", "RSF", "Data", "Diagnostics"])

with tabs[0]:
    left, right = st.columns(2)
    with left:
        show_image("Kaplan-Meier by Tumor Stage", FIGURES_DIR / "km_by_tumor_stage.png")
    with right:
        show_image("Kaplan-Meier by ER Status", FIGURES_DIR / "km_by_er_status.png")
    show_table("Log-Rank Results", logrank)

with tabs[1]:
    left, right = st.columns([1.1, 0.9])
    with left:
        show_image("Top Hazard Ratios", FIGURES_DIR / "cox_hazard_ratios.png")
    with right:
        show_table("Cox Model Performance", cox_metrics)
        show_table("Stratified Cox Sensitivity", cox_stratified_metrics)
    show_table("Cox Hazard Ratios", cox_hr)

with tabs[2]:
    left, right = st.columns(2)
    with left:
        show_image("RSF Feature Importance", FIGURES_DIR / "rsf_feature_importance.png")
    with right:
        show_image("RSF Calibration at 60 Months", FIGURES_DIR / "rsf_calibration_60_months.png")
    show_table("RSF Metrics", rsf_metrics)
    if rsf_metrics is not None and not rsf_metrics.empty:
        row = rsf_metrics.iloc[0]
        if {"test_c_index_ci_low", "test_c_index_ci_high"}.issubset(rsf_metrics.columns):
            st.caption(
                "RSF test C-index 95% CI: "
                f"{row['test_c_index_ci_low']:.3f} to {row['test_c_index_ci_high']:.3f}; "
                "mean time-dependent AUC 95% CI: "
                f"{row['time_dependent_auc_ci_low']:.3f} to {row['time_dependent_auc_ci_high']:.3f}."
            )
    show_table("RSF Calibration", rsf_calibration)
    show_table("RSF Feature Importance", rsf_importance)

with tabs[3]:
    show_table("Data Profile", data_profile)
    show_table("Cox Feature Missingness", cox_missingness)

with tabs[4]:
    st.subheader("Proportional Hazards Diagnostics")
    baseline_path = REPORTS_DIR / "cox_ph_assumptions.txt"
    stratified_path = REPORTS_DIR / "cox_stratified_ph_assumptions.txt"
    if baseline_path.exists():
        st.text_area("Baseline Cox PH Check", baseline_path.read_text(encoding="utf-8"), height=320)
    else:
        st.info("Baseline Cox PH diagnostics have not been generated.")

    if stratified_path.exists():
        st.text_area(
            "Stratified Cox Sensitivity PH Check",
            stratified_path.read_text(encoding="utf-8"),
            height=320,
        )
    else:
        st.info("Stratified Cox PH diagnostics have not been generated.")
