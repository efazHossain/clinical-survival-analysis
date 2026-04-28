"""
Train Random Survival Forest model.

Outputs:
- reports/rsf_metrics.csv
- reports/rsf_feature_importance.csv
- reports/figures/rsf_feature_importance.png
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.inspection import permutation_importance
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sksurv.ensemble import RandomSurvivalForest
from sksurv.metrics import concordance_index_censored


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT_DIR / "data" / "processed" / "metabric_survival_processed.csv"
REPORTS_DIR = ROOT_DIR / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"


RSF_FEATURES = [
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


def make_one_hot_encoder() -> OneHotEncoder:
    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        return OneHotEncoder(handle_unknown="ignore", sparse=False)


def prepare_survival_target(df: pd.DataFrame) -> np.ndarray:
    return np.array(
        [(bool(event), float(duration)) for event, duration in zip(df["event"], df["duration_months"])],
        dtype=[("event", "?"), ("time", "<f8")],
    )


def cindex_scorer(model, X, y) -> float:
    risk_scores = model.predict(X)
    return concordance_index_censored(y["event"], y["time"], risk_scores)[0]


def get_feature_names(preprocessor: ColumnTransformer) -> list[str]:
    try:
        return preprocessor.get_feature_names_out().tolist()
    except Exception:
        return [f"feature_{i}" for i in range(0)]


def main() -> None:
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Processed file not found: {DATA_PATH}\n"
            "Run: python src/prepare_data.py"
        )

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(DATA_PATH)

    available_features = [col for col in RSF_FEATURES if col in df.columns]
    model_df = df[["duration_months", "event"] + available_features].dropna(
        subset=["duration_months", "event"]
    )

    X = model_df[available_features]
    y = prepare_survival_target(model_df)

    numeric_cols = X.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = [col for col in X.columns if col not in numeric_cols]

    numeric_pipe = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipe = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", make_one_hot_encoder()),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_pipe, numeric_cols),
            ("cat", categorical_pipe, categorical_cols),
        ]
    )

    X_processed = preprocessor.fit_transform(X)
    feature_names = preprocessor.get_feature_names_out().tolist()

    X_train, X_test, y_train, y_test = train_test_split(
        X_processed,
        y,
        test_size=0.2,
        random_state=42,
    )

    rsf = RandomSurvivalForest(
        n_estimators=200,
        min_samples_split=10,
        min_samples_leaf=15,
        max_features="sqrt",
        n_jobs=-1,
        random_state=42,
    )

    print("Training Random Survival Forest...")
    rsf.fit(X_train, y_train)

    train_cindex = cindex_scorer(rsf, X_train, y_train)
    test_cindex = cindex_scorer(rsf, X_test, y_test)

    metrics = pd.DataFrame(
        [
            {
                "model": "Random Survival Forest",
                "train_c_index": train_cindex,
                "test_c_index": test_cindex,
                "n_train": len(X_train),
                "n_test": len(X_test),
                "n_features": X_processed.shape[1],
            }
        ]
    )

    metrics.to_csv(REPORTS_DIR / "rsf_metrics.csv", index=False)

    print("Calculating permutation importance...")
    X_small = X_test[: min(500, len(X_test))]
    y_small = y_test[: min(500, len(y_test))]

    perm = permutation_importance(
        rsf,
        X_small,
        y_small,
        scoring=cindex_scorer,
        n_repeats=5,
        random_state=42,
        n_jobs=1,
    )

    importance_df = pd.DataFrame(
        {
            "feature": feature_names,
            "importance_mean": perm.importances_mean,
            "importance_std": perm.importances_std,
        }
    ).sort_values("importance_mean", ascending=False)

    importance_df.to_csv(REPORTS_DIR / "rsf_feature_importance.csv", index=False)

    plot_df = importance_df.head(15).sort_values("importance_mean", ascending=True)

    plt.figure(figsize=(10, 7))
    plt.barh(plot_df["feature"], plot_df["importance_mean"])
    plt.xlabel("Permutation Importance Mean")
    plt.title("Random Survival Forest Feature Importance")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "rsf_feature_importance.png", dpi=300)
    plt.close()

    print("Random Survival Forest training complete.")
    print(metrics)
    print(f"Saved metrics to: {REPORTS_DIR / 'rsf_metrics.csv'}")
    print(f"Saved feature importance to: {REPORTS_DIR / 'rsf_feature_importance.csv'}")


if __name__ == "__main__":
    main()