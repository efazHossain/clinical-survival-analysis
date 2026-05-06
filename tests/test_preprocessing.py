from __future__ import annotations

import pandas as pd
import pytest

from config import SURVIVAL_STATUS_COL, SURVIVAL_TIME_COL
from preprocessing import clean_survival_data, parse_event, prepare_cox_data


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("0:LIVING", 0),
        ("1:DECEASED", 1),
        ("Dead", 1),
        ("living", 0),
        (pd.NA, 0),
    ],
)
def test_parse_event(value: object, expected: int) -> None:
    assert parse_event(value) == expected


def test_clean_survival_data_filters_invalid_durations_and_normalizes_missing_values() -> None:
    raw = pd.DataFrame(
        {
            "Patient ID": ["A", "B", "C"],
            SURVIVAL_TIME_COL: ["12", "0", "bad"],
            SURVIVAL_STATUS_COL: ["1:DECEASED", "0:LIVING", "0:LIVING"],
            "ER Status": ["Positive", "Unknown", "NA"],
        }
    )

    cleaned = clean_survival_data(raw, feature_columns=["ER Status"])

    assert cleaned.shape[0] == 1
    assert cleaned.loc[0, "duration_months"] == 12
    assert cleaned.loc[0, "event"] == 1
    assert cleaned.loc[0, "ER Status"] == "Positive"


def test_clean_survival_data_requires_survival_columns() -> None:
    with pytest.raises(ValueError, match="Missing survival time column"):
        clean_survival_data(pd.DataFrame({SURVIVAL_STATUS_COL: ["0:LIVING"]}))


def test_prepare_cox_data_keeps_rows_with_missing_predictors() -> None:
    df = pd.DataFrame(
        {
            "duration_months": [12.0, 24.0, 36.0],
            "event": [1, 0, 1],
            "Age at Diagnosis": [50.0, None, 60.0],
            "ER Status": ["Positive", None, "Negative"],
        }
    )

    cox_df, missingness = prepare_cox_data(df, ["Age at Diagnosis", "ER Status"])

    assert len(cox_df) == 3
    assert "ER Status_Positive" in cox_df.columns or "ER Status_Missing" in cox_df.columns
    assert missingness["missing_count"].sum() == 2
