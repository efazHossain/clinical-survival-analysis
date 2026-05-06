# Portfolio Case Study: Clinical Survival Analysis

## Summary

This project builds a reproducible survival-analysis workflow for METABRIC breast cancer clinical data. It combines classical survival statistics with machine learning to compare clinical groups, estimate relative survival risk, and document model limitations clearly.

## Problem

Clinical survival analysis often needs two complementary views:

- Interpretable statistical estimates for clinical variables such as age, tumor stage, receptor status, and treatment indicators.
- Flexible machine learning models that can capture nonlinear effects and interactions while still reporting model quality and calibration.

This project asks:

> Which clinical and tumor-related factors are associated with differences in overall survival?

## Approach

The pipeline prepares a canonical survival dataset, then runs:

- Kaplan-Meier survival curves for tumor stage and ER status.
- Log-rank tests for group-level survival differences.
- Cox proportional hazards modeling with missingness reporting and PH assumption diagnostics.
- Stratified Cox sensitivity modeling for variables flagged by PH checks.
- Random Survival Forest modeling with C-index, time-dependent AUC, integrated Brier score, calibration, and permutation feature importance.

## Current Results

| Output | Current Value |
|---|---:|
| Processed cohort size | 1,980 |
| Event count | 1,144 |
| Event rate | 57.8% |
| Tumor Stage log-rank p-value | 9.35e-27 |
| ER Status log-rank p-value | 0.035 |
| Cox PH C-index | 0.680 |
| RSF test C-index | 0.684 |
| RSF test C-index 95% CI | See `reports/rsf_metrics.csv` |
| RSF mean time-dependent AUC | 0.718 |
| RSF mean time-dependent AUC 95% CI | See `reports/rsf_metrics.csv` |
| RSF integrated Brier score | 0.177 |

## Engineering Work

The repository now includes:

- A one-command analysis pipeline: `make pipeline`
- Local quality checks: `make test` and `make compile`
- GitHub Actions CI for every push and pull request
- Pinned Python dependencies
- A Streamlit dashboard for reviewing model outputs
- A model card documenting intended use, limitations, and safety boundaries
- Bootstrap confidence intervals for held-out RSF C-index and time-dependent AUC
- Generated reproducibility metadata including package versions and raw-data SHA-256

## Interpretation

The results suggest meaningful survival differences across tumor stage and ER status groups. The Cox model provides interpretable hazard ratios, but proportional hazards diagnostics flag several variables, so the stratified Cox sensitivity model should be reviewed before treating those effects as stable over time.

The Random Survival Forest provides a slightly higher test C-index than the Cox model and adds calibration and feature-importance views. These outputs are useful for exploratory analysis, not clinical decision-making.

## Limitations

- The project uses a single cohort and does not include external validation.
- Missing survival status is currently encoded as non-event/censored.
- Model outputs are association-focused and should not be interpreted causally.
- Random Survival Forest feature importance is model-dependent.
- No clinical deployment workflow, governance review, or prospective validation is included.

## Next Improvements

- Add external validation on an independent survival cohort.
- Add cohort filters to the Streamlit dashboard.
- Add downloadable report exports from the dashboard.
- Add partial dependence or accumulated local effects for the Random Survival Forest.
