"""
Prepare METABRIC clinical survival data.

Inputs:
- data/raw/metabric_clinical_data.tsv

Outputs:
- data/processed/metabric_survival_processed.csv
- data/sample/metabric_sample.csv
- reports/data_profile.csv
- reports/runtime_versions.csv
"""

from __future__ import annotations

import pandas as pd

from config import (
    PROCESSED_DIR,
    PROCESSED_PATH,
    RANDOM_STATE,
    RAW_PATH,
    REPORTS_DIR,
    SAMPLE_DIR,
    SAMPLE_PATH,
    SAMPLE_SIZE,
)
from preprocessing import clean_survival_data
from survival_utils import event_summary, file_sha256, package_versions


def main() -> None:
    if not RAW_PATH.exists():
        raise FileNotFoundError(
            f"Raw file not found: {RAW_PATH}\n"
            "Place metabric_clinical_data.tsv in data/raw/"
        )

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(RAW_PATH, sep="\t")
    cleaned = clean_survival_data(df)

    cleaned.to_csv(PROCESSED_PATH, index=False)
    cleaned.sample(n=min(SAMPLE_SIZE, len(cleaned)), random_state=RANDOM_STATE).to_csv(
        SAMPLE_PATH,
        index=False,
    )

    profile = pd.DataFrame(
        [
            {
                "raw_rows": len(df),
                "raw_columns": len(df.columns),
                "processed_rows": len(cleaned),
                "processed_columns": len(cleaned.columns),
                "raw_sha256": file_sha256(RAW_PATH),
                **event_summary(cleaned),
            }
        ]
    )
    profile.to_csv(REPORTS_DIR / "data_profile.csv", index=False)

    package_versions(
        [
            "pandas",
            "numpy",
            "matplotlib",
            "seaborn",
            "scikit-learn",
            "lifelines",
            "scikit-survival",
            "streamlit",
        ]
    ).to_csv(REPORTS_DIR / "runtime_versions.csv", index=False)

    print(f"Raw shape: {df.shape}")
    print(f"Processed shape: {cleaned.shape}")
    print(f"Events: {cleaned['event'].sum()} / {len(cleaned)}")
    print(f"Saved processed data to: {PROCESSED_PATH}")
    print(f"Saved sample data to: {SAMPLE_PATH}")
    print(f"Saved data profile to: {REPORTS_DIR / 'data_profile.csv'}")


if __name__ == "__main__":
    main()
