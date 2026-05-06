"""Reusable preprocessing helpers for METABRIC survival modeling."""

from __future__ import annotations

import pandas as pd

from config import (
    FEATURE_COLUMNS,
    MISSING_VALUES,
    PATIENT_ID_COL,
    SURVIVAL_STATUS_COL,
    SURVIVAL_TIME_COL,
)


TARGET_COLUMNS = ["duration_months", "event"]


def parse_event(value: object) -> int:
    """Convert a METABRIC survival status value into a binary event indicator."""
    if pd.isna(value):
        return 0

    text = str(value).strip().upper()
    if text.startswith("1") or "DECEASED" in text or "DEAD" in text:
        return 1

    return 0


def available_columns(df: pd.DataFrame, columns: list[str]) -> list[str]:
    """Return requested columns that exist in the dataframe, preserving order."""
    return [col for col in columns if col in df.columns]


def normalize_missing_values(df: pd.DataFrame, protected_cols: list[str] | None = None) -> pd.DataFrame:
    """Replace common string placeholders with pandas missing values."""
    cleaned = df.copy()
    protected = set(protected_cols or [])

    for col in cleaned.columns:
        if col not in protected:
            cleaned[col] = cleaned[col].replace(MISSING_VALUES, pd.NA)

    return cleaned


def clean_survival_data(df: pd.DataFrame, feature_columns: list[str] | None = None) -> pd.DataFrame:
    """Create the canonical modeling dataset from raw METABRIC clinical data."""
    if SURVIVAL_TIME_COL not in df.columns:
        raise ValueError(f"Missing survival time column: {SURVIVAL_TIME_COL}")

    if SURVIVAL_STATUS_COL not in df.columns:
        raise ValueError(f"Missing survival status column: {SURVIVAL_STATUS_COL}")

    cleaned = df.copy()
    cleaned["duration_months"] = pd.to_numeric(cleaned[SURVIVAL_TIME_COL], errors="coerce")
    cleaned["event"] = cleaned[SURVIVAL_STATUS_COL].apply(parse_event)

    features = available_columns(cleaned, feature_columns or FEATURE_COLUMNS)
    id_cols = [PATIENT_ID_COL] if PATIENT_ID_COL in cleaned.columns else []
    keep_cols = id_cols + TARGET_COLUMNS + features

    cleaned = cleaned[keep_cols].copy()
    cleaned = normalize_missing_values(cleaned, protected_cols=id_cols + TARGET_COLUMNS)
    cleaned = cleaned.dropna(subset=["duration_months"])
    cleaned = cleaned[cleaned["duration_months"] > 0]

    return cleaned


def missingness_report(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Summarize missing values for selected columns."""
    available = available_columns(df, columns)
    rows = []

    for col in available:
        missing_count = int(df[col].isna().sum())
        rows.append(
            {
                "column": col,
                "missing_count": missing_count,
                "missing_rate": missing_count / len(df) if len(df) else 0.0,
            }
        )

    return pd.DataFrame(rows)


def prepare_cox_data(
    df: pd.DataFrame,
    feature_columns: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Prepare a Cox PH modeling matrix and a missingness report.

    Numeric predictors are median-imputed and categorical predictors get an
    explicit Missing level before one-hot encoding. This avoids silently
    changing the cohort through complete-case deletion.
    """
    features = available_columns(df, feature_columns)
    model_df = df[TARGET_COLUMNS + features].copy()
    model_df = normalize_missing_values(model_df, protected_cols=TARGET_COLUMNS)
    model_df = model_df.dropna(subset=TARGET_COLUMNS)

    feature_missingness = missingness_report(model_df, features)

    for col in features:
        numeric = pd.to_numeric(model_df[col], errors="coerce")
        if numeric.notna().sum() >= model_df[col].notna().sum() * 0.9:
            model_df[col] = numeric.fillna(numeric.median())
        else:
            model_df[col] = model_df[col].fillna("Missing")

    categorical_cols = model_df.select_dtypes(include=["object", "category"]).columns.tolist()
    model_df = pd.get_dummies(model_df, columns=categorical_cols, drop_first=True)

    for col in model_df.columns:
        model_df[col] = pd.to_numeric(model_df[col], errors="coerce")

    model_df = model_df.dropna(subset=TARGET_COLUMNS)

    return model_df, feature_missingness
