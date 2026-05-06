from __future__ import annotations

import pandas as pd

from survival_utils import event_summary, prepare_survival_target


def test_prepare_survival_target_uses_sksurv_structured_dtype() -> None:
    df = pd.DataFrame({"event": [1, 0], "duration_months": [10.0, 20.0]})

    target = prepare_survival_target(df)

    assert target.dtype.names == ("event", "time")
    assert target["event"].tolist() == [True, False]
    assert target["time"].tolist() == [10.0, 20.0]


def test_event_summary_reports_event_rate() -> None:
    df = pd.DataFrame({"event": [1, 0, 1]})

    summary = event_summary(df)

    assert summary["n_rows"] == 3
    assert summary["n_events"] == 2
    assert summary["event_rate"] == 2 / 3
