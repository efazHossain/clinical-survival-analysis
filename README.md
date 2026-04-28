# Clinical Survival Analysis

A survival analysis and machine learning project using METABRIC breast cancer clinical data to model patient survival risk, compare clinical groups, and identify key predictors of overall survival.

## Project Overview

This project applies statistical survival analysis and machine learning methods to breast cancer clinical data. The goal is to understand which patient and tumor characteristics are associated with survival outcomes and to build interpretable models that estimate patient risk over time.

The project combines traditional survival analysis with machine learning methods, including Kaplan-Meier curves, log-rank tests, Cox proportional hazards modeling, and Random Survival Forests.

## Clinical Question

Which clinical and tumor-related factors are associated with differences in overall survival?

## Tech Stack

| Category | Tools |
|---|---|
| Programming | Python |
| Data Analysis | pandas, NumPy |
| Visualization | Matplotlib, Seaborn |
| Survival Analysis | lifelines, scikit-survival |
| Machine Learning | scikit-learn, Random Survival Forest |
| Reporting | Jupyter Notebook, Markdown |

## Methods

- Exploratory data analysis
- Kaplan-Meier survival curves
- Log-rank hypothesis testing
- Cox proportional hazards modeling
- Proportional hazards assumption checks
- Random Survival Forest modeling
- Feature importance analysis

## Key Results

| Analysis | Result |
|---|---|
| Tumor Stage log-rank test | p = 9.35e-27 |
| ER Status log-rank test | p = 0.035 |
| Random Survival Forest train C-index | 0.739 |
| Random Survival Forest test C-index | 0.681 |
| RSF feature count | 34 features |

## Model Interpretation

The Cox proportional hazards model identified several clinically relevant survival predictors, including:

- Age at diagnosis
- Tumor stage
- HER2 status
- Lymph nodes examined positive
- Nottingham prognostic index
- Radio therapy status

The Random Survival Forest model was used to capture nonlinear survival patterns and rank patients by relative survival risk.

## Project Structure

```text
clinical-survival-analysis/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── sample/
│
├── notebooks/
│   ├── 01_eda_km_logrank.ipynb
│   ├── 02_cox_model.ipynb
│   └── 03_ml_survival_rsf.ipynb
│
├── src/
│   ├── prepare_data.py
│   ├── run_kaplan_meier.py
│   ├── train_cox_model.py
│   ├── train_random_survival_forest.py
│   ├── evaluate_models.py
│   ├── preprocessing.py
│   └── survival_utils.py
│
├── reports/
│   ├── figures/
│   ├── cox_hazard_ratios.csv
│   ├── cox_model_summary.csv
│   ├── logrank_results.csv
│   ├── model_results_summary.md
│   ├── rsf_feature_importance.csv
│   └── rsf_metrics.csv
│
├── requirements.txt
└── README.md
```

## Reproducible Pipeline

Run the full analysis pipeline:

```bash
python src/prepare_data.py
python src/run_kaplan_meier.py
python src/train_cox_model.py
python src/train_random_survival_forest.py
python src/evaluate_models.py
```

## Outputs

The pipeline generates:

- Cleaned survival modeling dataset
- Kaplan-Meier survival plots
- Log-rank test results
- Cox model hazard ratios
- Random Survival Forest C-index metrics
- RSF feature importance report
- Consolidated clinical survival summary

## Limitations

This project is for analytical and educational purposes only. Results should not be interpreted as clinical guidance. Survival models may be affected by missingness, censoring patterns, cohort bias, and proportional hazards assumptions.

## Future Improvements

- Add model calibration analysis
- Add time-dependent AUC evaluation
- Add partial dependence plots for Random Survival Forest predictions
- Build a lightweight Streamlit dashboard for interactive survival-risk exploration
- Add a formal model card covering intended use, limitations, and ethical considerations
