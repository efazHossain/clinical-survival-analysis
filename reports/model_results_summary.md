# Clinical Survival Analysis Summary

## Objective

Analyze breast cancer patient survival outcomes using Kaplan-Meier curves, log-rank testing, Cox proportional hazards modeling, and Random Survival Forests.

## Data Profile

|   raw_rows |   raw_columns |   processed_rows |   processed_columns | raw_sha256                                                       |   n_rows |   n_events |   event_rate |
|-----------:|--------------:|-----------------:|--------------------:|:-----------------------------------------------------------------|---------:|-----------:|-------------:|
|       2509 |            39 |             1980 |                  21 | bfa894af00c08907c19f1ab549c89d625981a31b4dd737a313e0a32caff237ee |     1980 |       1144 |     0.577778 |

## Log-Rank Test Results

| group_variable   |   test_statistic |     p_value |    n |   n_events |   n_groups |
|:-----------------|-----------------:|------------:|-----:|-----------:|-----------:|
| Tumor Stage      |         128.221  | 9.34906e-27 | 1466 |        823 |          5 |
| ER Status        |           4.4429 | 0.0350467   | 1980 |       1144 |          2 |

## Cox Model Performance

| model                    |   concordance_index |   n_rows |   n_events |   n_features |   penalizer |
|:-------------------------|--------------------:|---------:|-----------:|-------------:|------------:|
| Cox proportional hazards |            0.679583 |     1980 |       1144 |           17 |         0.1 |

## Stratified Cox Sensitivity Performance

| model                      |   concordance_index |   n_rows |   n_events |   n_features |   penalizer | strata                                                     |
|:---------------------------|--------------------:|---------:|-----------:|-------------:|------------:|:-----------------------------------------------------------|
| Stratified Cox sensitivity |            0.588423 |     1980 |       1144 |           13 |         0.1 | age_group; npi_group; tumor_stage_strata; er_status_strata |

## Random Survival Forest Performance

| model                  |   train_c_index |   test_c_index |   n_train |   n_test |   n_train_events |   n_test_events |   n_features |   time_dependent_auc_mean |   integrated_brier_score |   bootstrap_repeats |   bootstrap_skipped |   test_c_index_ci_low |   test_c_index_ci_high |   time_dependent_auc_ci_low |   time_dependent_auc_ci_high |
|:-----------------------|----------------:|---------------:|----------:|---------:|-----------------:|----------------:|-------------:|--------------------------:|-------------------------:|--------------------:|--------------------:|----------------------:|-----------------------:|----------------------------:|-----------------------------:|
| Random Survival Forest |        0.738995 |       0.684117 |      1584 |      396 |              915 |             229 |           34 |                  0.718181 |                  0.17673 |                 300 |                   0 |              0.649678 |               0.719025 |                    0.677125 |                     0.766394 |

## RSF Bootstrap Confidence Intervals

- Test C-index 95% CI: 0.650 to 0.719.
- Mean time-dependent AUC 95% CI: 0.677 to 0.766.
- Bootstrap repeats: 300; skipped resamples: 0.

## Top Cox Model Hazard Ratios

| covariate                   |       coef |   exp(coef) |           p |   coef lower 95% |   coef upper 95% |
|:----------------------------|-----------:|------------:|------------:|-----------------:|-----------------:|
| Tumor Stage                 |  0.201227  |    1.2229   | 0.000513845 |        0.08768   |        0.314774  |
| HER2 Status_Positive        |  0.136455  |    1.1462   | 0.38453     |       -0.171104  |        0.444014  |
| HER2 Status_Negative        | -0.139038  |    0.870195 | 0.374318    |       -0.445776  |        0.167699  |
| Radio Therapy_NO            |  0.120641  |    1.12822  | 0.256031    |       -0.0875358 |        0.328817  |
| Radio Therapy_YES           | -0.12198   |    0.885166 | 0.250681    |       -0.330109  |        0.0861487 |
| Nottingham prognostic index |  0.106627  |    1.11252  | 0.00127779  |        0.0417434 |        0.171511  |
| Chemotherapy_YES            |  0.10477   |    1.11046  | 0.425836    |       -0.153092  |        0.362632  |
| Chemotherapy_NO             | -0.106611  |    0.898876 | 0.416437    |       -0.363746  |        0.150525  |
| ER Status_Positive          | -0.0691498 |    0.933187 | 0.407189    |       -0.232667  |        0.0943673 |
| Neoplasm Histologic Grade   |  0.0625361 |    1.06453  | 0.22632     |       -0.0387692 |        0.163841  |

## Cox Feature Missingness

| column                        |   missing_count |   missing_rate |
|:------------------------------|----------------:|---------------:|
| Tumor Stage                   |             514 |    0.259596    |
| Neoplasm Histologic Grade     |              87 |    0.0439394   |
| Lymph nodes examined positive |              76 |    0.0383838   |
| Tumor Size                    |              25 |    0.0126263   |
| Radio Therapy                 |               1 |    0.000505051 |
| Nottingham prognostic index   |               1 |    0.000505051 |
| Chemotherapy                  |               1 |    0.000505051 |
| Hormone Therapy               |               1 |    0.000505051 |
| PR Status                     |               1 |    0.000505051 |
| HER2 Status                   |               1 |    0.000505051 |
| Age at Diagnosis              |               0 |    0           |
| ER Status                     |               0 |    0           |

## Diagnostics and Artifacts

- Cox proportional hazards assumption output: `reports/cox_ph_assumptions.txt`.
- Stratified Cox sensitivity output: `reports/cox_stratified_ph_assumptions.txt`.
- RSF calibration table: `reports/rsf_calibration.csv`.
- Fitted model artifacts are written to `models/` and ignored by Git.

## Cox Diagnostic Handling

The baseline Cox assumption check flagged age, ER status, Nottingham prognostic index, and tumor stage. A stratified sensitivity model bins age and Nottingham prognostic index and stratifies by those bins plus ER status and tumor stage. Use the baseline Cox model for coefficient-level interpretation, then compare the stratified sensitivity model before treating those flagged terms as stable proportional hazards.

## Interpretation

- Kaplan-Meier curves compare survival probability across clinical groups.
- Log-rank tests evaluate whether survival differences between groups are statistically significant.
- Cox proportional hazards modeling provides interpretable hazard ratios; assumption checks should be reviewed before relying on any coefficient.
- Random Survival Forests capture nonlinear survival patterns and provide model-based risk ranking.

## Limitations

- This project is for analytical and educational purposes only.
- Results should not be interpreted as clinical guidance.
- Missing survival status is currently encoded as non-event/censored during preprocessing; review this assumption before clinical interpretation.
- Survival models may be affected by missingness, censoring patterns, cohort bias, and proportional hazards assumptions.

## Runtime Versions

| package         | version   |
|:----------------|:----------|
| pandas          | 2.3.3     |
| numpy           | 2.4.0     |
| matplotlib      | 3.10.8    |
| seaborn         | 0.13.2    |
| scikit-learn    | 1.7.2     |
| lifelines       | 0.30.0    |
| scikit-survival | 0.26.0    |
| streamlit       | 1.57.0    |
