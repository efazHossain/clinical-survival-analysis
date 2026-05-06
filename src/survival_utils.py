"""Survival-modeling utilities shared across scripts and tests."""

from __future__ import annotations

import hashlib
import importlib.metadata
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from sksurv.metrics import concordance_index_censored


def ensure_numpy_trapz_compat() -> None:
    """Restore np.trapz alias for libraries that have not moved to np.trapezoid."""
    if not hasattr(np, "trapz") and hasattr(np, "trapezoid"):
        np.trapz = np.trapezoid  # type: ignore[attr-defined]


def make_one_hot_encoder() -> OneHotEncoder:
    """Create a dense one-hot encoder across supported scikit-learn versions."""
    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        return OneHotEncoder(handle_unknown="ignore", sparse=False)


def prepare_survival_target(df: pd.DataFrame) -> np.ndarray:
    """Create a scikit-survival structured target array."""
    return np.array(
        [(bool(event), float(duration)) for event, duration in zip(df["event"], df["duration_months"])],
        dtype=[("event", "?"), ("time", "<f8")],
    )


def cindex_scorer(model, X, y) -> float:
    """Score a survival estimator with Harrell's concordance index."""
    risk_scores = model.predict(X)
    return float(concordance_index_censored(y["event"], y["time"], risk_scores)[0])


def file_sha256(path: Path) -> str | None:
    """Return a file SHA-256 hash, or None when the file does not exist."""
    if not path.exists():
        return None

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def package_versions(packages: list[str]) -> pd.DataFrame:
    """Return installed package versions for reproducibility reporting."""
    rows = []
    for package in packages:
        try:
            version = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            version = "not-installed"
        rows.append({"package": package, "version": version})

    return pd.DataFrame(rows)


def event_summary(df: pd.DataFrame) -> dict[str, float | int]:
    """Summarize survival cohort size and event rate."""
    n_rows = int(len(df))
    n_events = int(df["event"].sum()) if "event" in df else 0
    return {
        "n_rows": n_rows,
        "n_events": n_events,
        "event_rate": n_events / n_rows if n_rows else 0.0,
    }
