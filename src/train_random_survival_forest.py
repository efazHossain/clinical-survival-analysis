"""
Train Random Survival Forest model.

Outputs:
- reports/rsf_metrics.csv
- reports/rsf_feature_importance.csv
- reports/rsf_calibration.csv
- reports/figures/rsf_feature_importance.png
- reports/figures/rsf_calibration_60_months.png
- models/random_survival_forest.joblib
"""

from __future__ import annotations

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from lifelines import KaplanMeierFitter
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sksurv.ensemble import RandomSurvivalForest
from sksurv.metrics import cumulative_dynamic_auc, integrated_brier_score

from config import (
    FIGURES_DIR,
    MODELS_DIR,
    PROCESSED_PATH,
    RANDOM_STATE,
    REPORTS_DIR,
    RSF_FEATURES,
    TEST_SIZE,
)
from preprocessing import available_columns
from survival_utils import (
    cindex_scorer,
    ensure_numpy_trapz_compat,
    make_one_hot_encoder,
    prepare_survival_target,
)


ensure_numpy_trapz_compat()


def build_preprocessor(X: pd.DataFrame) -> ColumnTransformer:
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

    return ColumnTransformer(
        transformers=[
            ("num", numeric_pipe, numeric_cols),
            ("cat", categorical_pipe, categorical_cols),
        ]
    )


def evaluation_times(y_train: np.ndarray, y_test: np.ndarray, n_times: int = 12) -> np.ndarray:
    lower = max(float(np.min(y_train["time"])), float(np.min(y_test["time"])))
    upper = min(float(np.max(y_train["time"])), float(np.max(y_test["time"])))
    event_times = y_test["time"][y_test["event"]]
    event_times = event_times[(event_times > lower) & (event_times < upper)]

    if len(event_times) < 2:
        return np.array([])

    quantiles = np.linspace(0.1, 0.9, n_times)
    return np.unique(np.quantile(event_times, quantiles))


def survival_metric_summary(
    rsf: RandomSurvivalForest,
    X_test: np.ndarray,
    y_train: np.ndarray,
    y_test: np.ndarray,
) -> dict[str, float]:
    times = evaluation_times(y_train, y_test)
    metrics = {
        "time_dependent_auc_mean": np.nan,
        "integrated_brier_score": np.nan,
    }

    if len(times) == 0:
        return metrics

    try:
        risk_scores = rsf.predict(X_test)
        _, mean_auc = cumulative_dynamic_auc(y_train, y_test, risk_scores, times)
        metrics["time_dependent_auc_mean"] = float(mean_auc)
    except Exception:
        pass

    try:
        surv_funcs = rsf.predict_survival_function(X_test)
        survival_probabilities = np.vstack([fn(times) for fn in surv_funcs])
        metrics["integrated_brier_score"] = float(
            integrated_brier_score(y_train, y_test, survival_probabilities, times)
        )
    except Exception:
        pass

    return metrics


def calibration_table(
    rsf: RandomSurvivalForest,
    X_test: np.ndarray,
    y_test: np.ndarray,
    horizon_months: float = 60.0,
) -> pd.DataFrame:
    surv_funcs = rsf.predict_survival_function(X_test)
    predicted_survival = np.array([fn(horizon_months) for fn in surv_funcs])

    cal_df = pd.DataFrame(
        {
            "duration_months": y_test["time"],
            "event": y_test["event"],
            "predicted_survival": predicted_survival,
        }
    )
    cal_df["risk_bin"] = pd.qcut(
        1.0 - cal_df["predicted_survival"],
        q=min(5, cal_df["predicted_survival"].nunique()),
        duplicates="drop",
    )

    kmf = KaplanMeierFitter()
    rows = []
    for risk_bin, group_df in cal_df.groupby("risk_bin", observed=True):
        kmf.fit(group_df["duration_months"], event_observed=group_df["event"])
        rows.append(
            {
                "risk_bin": str(risk_bin),
                "n": len(group_df),
                "predicted_survival_mean": group_df["predicted_survival"].mean(),
                "observed_survival_km": float(kmf.survival_function_at_times(horizon_months).iloc[0]),
                "horizon_months": horizon_months,
            }
        )

    return pd.DataFrame(rows)


def plot_calibration(calibration: pd.DataFrame) -> None:
    if calibration.empty:
        return

    plt.figure(figsize=(7, 6))
    plt.scatter(calibration["predicted_survival_mean"], calibration["observed_survival_km"])
    plt.plot([0, 1], [0, 1], linestyle="--")
    plt.xlabel("Predicted survival probability")
    plt.ylabel("Observed KM survival probability")
    plt.title("RSF Calibration at 60 Months")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "rsf_calibration_60_months.png", dpi=300)
    plt.close()


def main() -> None:
    if not PROCESSED_PATH.exists():
        raise FileNotFoundError(
            f"Processed file not found: {PROCESSED_PATH}\n"
            "Run: python src/prepare_data.py"
        )

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(PROCESSED_PATH)
    available_features = available_columns(df, RSF_FEATURES)
    model_df = df[["duration_months", "event"] + available_features].dropna(
        subset=["duration_months", "event"]
    )

    X = model_df[available_features]
    y = prepare_survival_target(model_df)

    preprocessor = build_preprocessor(X)
    X_processed = preprocessor.fit_transform(X)
    feature_names = preprocessor.get_feature_names_out().tolist()

    event_values = model_df["event"].astype(int)
    stratify = event_values if event_values.value_counts().min() >= 2 else None
    X_train, X_test, y_train, y_test = train_test_split(
        X_processed,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=stratify,
    )

    rsf = RandomSurvivalForest(
        n_estimators=200,
        min_samples_split=10,
        min_samples_leaf=15,
        max_features="sqrt",
        n_jobs=-1,
        random_state=RANDOM_STATE,
    )

    print("Training Random Survival Forest...")
    rsf.fit(X_train, y_train)

    train_cindex = cindex_scorer(rsf, X_train, y_train)
    test_cindex = cindex_scorer(rsf, X_test, y_test)
    survival_metrics = survival_metric_summary(rsf, X_test, y_train, y_test)

    metrics = pd.DataFrame(
        [
            {
                "model": "Random Survival Forest",
                "train_c_index": train_cindex,
                "test_c_index": test_cindex,
                "n_train": len(X_train),
                "n_test": len(X_test),
                "n_train_events": int(y_train["event"].sum()),
                "n_test_events": int(y_test["event"].sum()),
                "n_features": X_processed.shape[1],
                **survival_metrics,
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
        random_state=RANDOM_STATE,
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

    calibration = calibration_table(rsf, X_test, y_test)
    calibration.to_csv(REPORTS_DIR / "rsf_calibration.csv", index=False)
    plot_calibration(calibration)

    joblib.dump(
        {
            "preprocessor": preprocessor,
            "model": rsf,
            "features": available_features,
            "encoded_features": feature_names,
        },
        MODELS_DIR / "random_survival_forest.joblib",
    )

    print("Random Survival Forest training complete.")
    print(metrics)
    print(f"Saved metrics to: {REPORTS_DIR / 'rsf_metrics.csv'}")
    print(f"Saved feature importance to: {REPORTS_DIR / 'rsf_feature_importance.csv'}")
    print(f"Saved calibration to: {REPORTS_DIR / 'rsf_calibration.csv'}")
    print(f"Saved model artifact to: {MODELS_DIR / 'random_survival_forest.joblib'}")


if __name__ == "__main__":
    main()
