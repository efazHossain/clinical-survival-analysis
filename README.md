# Clinical Survival Analysis

A survival analysis and machine learning project using METABRIC breast cancer clinical data to model patient survival risk, compare clinical groups, and identify key predictors of overall survival.

## Project Overview

This project applies statistical survival analysis and machine learning methods to clinical breast cancer data. The goal is to understand which patient and tumor characteristics are associated with survival outcomes and to build interpretable models that estimate patient risk over time.

## Clinical Question

Which clinical and tumor-related factors are associated with differences in overall survival?

## Methods

- Exploratory data analysis
- Kaplan-Meier survival curves
- Log-rank hypothesis testing
- Cox proportional hazards modeling
- Proportional hazards assumption checks
- Random Survival Forest modeling
- Feature importance analysis

## Tech Stack

| Category | Tools |
|---|---|
| Programming | Python |
| Data Analysis | pandas, NumPy |
| Visualization | Matplotlib, Seaborn |
| Survival Analysis | lifelines, scikit-survival |
| Machine Learning | scikit-learn, Random Survival Forest |
| Reporting | Jupyter Notebook, Markdown |

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
│   ├── preprocessing.py
│   └── survival_utils.py
│
├── reports/
│   └── figures/
│
├── requirements.txt
└── README.md
