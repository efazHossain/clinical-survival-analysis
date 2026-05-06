"""Shared project configuration for the survival analysis pipeline."""

from __future__ import annotations

from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
SAMPLE_DIR = DATA_DIR / "sample"
REPORTS_DIR = ROOT_DIR / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
MODELS_DIR = ROOT_DIR / "models"

RAW_PATH = RAW_DIR / "metabric_clinical_data.tsv"
PROCESSED_PATH = PROCESSED_DIR / "metabric_survival_processed.csv"
SAMPLE_PATH = SAMPLE_DIR / "metabric_sample.csv"

SURVIVAL_TIME_COL = "Overall Survival (Months)"
SURVIVAL_STATUS_COL = "Overall Survival Status"
PATIENT_ID_COL = "Patient ID"

RANDOM_STATE = 42
SAMPLE_SIZE = 50
TEST_SIZE = 0.2

MISSING_VALUES = ["", "NA", "N/A", "Unknown", "unknown", "Not Available", "Not Performed"]

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

RSF_FEATURES = FEATURE_COLUMNS
