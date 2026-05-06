# Model Card: Clinical Survival Analysis

## Intended Use

This project is an educational and analytical survival-modeling workflow for METABRIC breast cancer clinical data. It is intended to demonstrate Kaplan-Meier analysis, log-rank testing, Cox proportional hazards modeling, Random Survival Forest modeling, and reproducible model reporting.

It is not intended for clinical decision support, patient triage, diagnosis, treatment selection, or individual medical guidance.

## Data

The pipeline expects METABRIC clinical data at `data/raw/metabric_clinical_data.tsv`.

The current reproduced run used:

- Raw rows: 2,509
- Processed rows: 1,980
- Events: 1,144
- Event rate: 57.8%
- Raw SHA-256: `bfa894af00c08907c19f1ab549c89d625981a31b4dd737a313e0a32caff237ee`

Raw and processed data are ignored by Git. Reproducibility metadata is written to `reports/data_profile.csv` and `reports/runtime_versions.csv`.

## Models

### Kaplan-Meier and Log-Rank Tests

Kaplan-Meier curves compare survival distributions across tumor stage and ER status groups. Log-rank tests quantify whether observed survival differences across groups are statistically distinguishable.

### Cox Proportional Hazards

The baseline Cox model estimates interpretable hazard ratios. Missing numeric predictors are median-imputed, categorical predictors receive an explicit missing level, and a modest penalizer is used.

The baseline PH diagnostic check flags age, ER status, Nottingham prognostic index, and tumor stage. The pipeline also trains a stratified Cox sensitivity model that bins age and Nottingham prognostic index and stratifies by those bins plus ER status and tumor stage.

### Random Survival Forest

The Random Survival Forest captures nonlinear interactions and ranks relative survival risk. It reports train/test C-index, time-dependent AUC, integrated Brier score, feature importance, and 60-month calibration.

## Performance From Current Run

| Model | Metric | Value |
|---|---:|---:|
| Cox PH | C-index | 0.680 |
| RSF | Test C-index | 0.684 |
| RSF | Mean time-dependent AUC | 0.718 |
| RSF | Integrated Brier score | 0.177 |

## Limitations

- Results are cohort-specific and may not generalize to other populations, institutions, collection periods, or cancer subtypes.
- Missing survival status is currently encoded as non-event/censored during preprocessing; this assumption should be reviewed before interpretation.
- Censoring patterns, missingness, and measurement practices can bias survival estimates.
- Cox coefficients should be interpreted alongside proportional hazards diagnostics.
- Random Survival Forest feature importance is model-dependent and not causal evidence.
- This repository does not validate predictions on an external cohort.

## Ethical and Safety Notes

This project should be described as a survival-analysis portfolio project, not a deployed clinical system. Any clinical use would require data governance review, external validation, calibration review, subgroup analysis, prospective evaluation, monitoring, and clinician oversight.

## Reproducibility

Run:

```bash
python src/pipeline.py
pytest
```

Generated model artifacts are saved under `models/` and ignored by Git.
