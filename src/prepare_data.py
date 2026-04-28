"""
Prepare METABRIC clinical survival data.

Inputs:
- data/raw/metabric_clinical_data.tsv

Outputs:
- data/processed/metabric_survival_processed.csv
- data/sample/metabric_sample.csv
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT_DIR / "data" / "raw" / "metabric_clinical_data.tsv"
PROCESSED_DIR = ROOT_DIR / "data" / "processed"
SAMPLE_DIR = ROOT_DIR / "data" / "sample"

OUTPUT_PATH = PROCESSED_DIR / "metabric_survival_processed.csv"
SAMPLE_PATH = SAMPLE_DIR / "metabric_sample.csv"


SURVIVAL_TIME_COL = "Overall Survival (Months)"
SURVIVAL_STATUS_COL = "Overall Survival Status"


FEATURE_COLUMNS = [
    "Age at Diagnosis",
    "Type of Breast Surgery",
    "Cellularity",
    "Chemotherapy",
    "Pam50 + Claudin-low subtype",
    "ER Status",
    "Neoplasm Histologic Grade",
    "HER2 Status",
    "Hormone Therapy",
    "Inferred Menopausal State",
    "Lymph nodes examined positive",
    "Mutation Count",
    "Nottingham prognostic index",
    "PR Status",
    "Radio Therapy",
    "TMB (nonsynonymous)",
    "Tumor Size",
    "Tumor Stage",
]


def parse_event(value: object) -> int:
    """
    Convert METABRIC survival status into binary event indicator.

    Expected examples:
    - "0:LIVING" -> 0
    - "1:DECEASED" -> 1
    """
    if pd.isna(value):
        return 0

    text = str(value).strip().upper()

    if text.startswith("1") or "DECEASED" in text or "DEAD" in text:
        return 1

    return 0


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    if SURVIVAL_TIME_COL not in df.columns:
        raise ValueError(f"Missing survival time column: {SURVIVAL_TIME_COL}")

    if SURVIVAL_STATUS_COL not in df.columns:
        raise ValueError(f"Missing survival status column: {SURVIVAL_STATUS_COL}")

    df["duration_months"] = pd.to_numeric(df[SURVIVAL_TIME_COL], errors="coerce")
    df["event"] = df[SURVIVAL_STATUS_COL].apply(parse_event)

    available_features = [col for col in FEATURE_COLUMNS if col in df.columns]

    keep_cols = ["Patient ID", "duration_months", "event"] + available_features
    keep_cols = [col for col in keep_cols if col in df.columns]

    cleaned = df[keep_cols].copy()

    cleaned = cleaned.dropna(subset=["duration_months"])
    cleaned = cleaned[cleaned["duration_months"] > 0]

    for col in cleaned.columns:
        if col not in ["Patient ID", "duration_months", "event"]:
            cleaned[col] = cleaned[col].replace(["", "NA", "N/A", "Unknown"], pd.NA)

    return cleaned


def main() -> None:
    if not RAW_PATH.exists():
        raise FileNotFoundError(
            f"Raw file not found: {RAW_PATH}\n"
            "Place metabric_clinical_data.tsv in data/raw/"
        )

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(RAW_PATH, sep="\t")
    cleaned = clean_data(df)

    cleaned.to_csv(OUTPUT_PATH, index=False)
    cleaned.sample(n=min(50, len(cleaned)), random_state=42).to_csv(SAMPLE_PATH, index=False)

    print(f"Raw shape: {df.shape}")
    print(f"Processed shape: {cleaned.shape}")
    print(f"Events: {cleaned['event'].sum()} / {len(cleaned)}")
    print(f"Saved processed data to: {OUTPUT_PATH}")
    print(f"Saved sample data to: {SAMPLE_PATH}")


if __name__ == "__main__":
    main()