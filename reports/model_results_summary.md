# Clinical Survival Analysis Summary

## Objective

Analyze breast cancer patient survival outcomes using Kaplan-Meier curves, log-rank testing, Cox proportional hazards modeling, and Random Survival Forests.

## Log-Rank Test Results

| group_variable   |   test_statistic |     p_value |    n |
|:-----------------|-----------------:|------------:|-----:|
| Tumor Stage      |         128.221  | 9.34906e-27 | 1466 |
| ER Status        |           4.4429 | 0.0350467   | 1980 |

## Random Survival Forest Performance

| model                  |   train_c_index |   test_c_index |   n_train |   n_test |   n_features |
|:-----------------------|----------------:|---------------:|----------:|---------:|-------------:|
| Random Survival Forest |        0.738811 |       0.681294 |      1584 |      396 |           34 |

## Top Cox Model Hazard Ratios

| covariate                     |       coef |   exp(coef) |           p |   coef lower 95% |   coef upper 95% |
|:------------------------------|-----------:|------------:|------------:|-----------------:|-----------------:|
| HER2 Status_Positive          |  0.306657  |    1.35887  | 0.00340196  |        0.101446  |        0.511868  |
| Tumor Stage                   |  0.182339  |    1.20002  | 0.00673883  |        0.05044   |        0.314238  |
| Radio Therapy_YES             | -0.218434  |    0.803777 | 0.00284953  |       -0.361929  |       -0.074938  |
| Nottingham prognostic index   |  0.138268  |    1.14828  | 0.00873526  |        0.0349212 |        0.241614  |
| ER Status_Positive            | -0.130944  |    0.877267 | 0.190743    |       -0.3271    |        0.0652107 |
| Hormone Therapy_YES           | -0.124323  |    0.883094 | 0.113474    |       -0.278275  |        0.029628  |
| Lymph nodes examined positive |  0.0429841 |    1.04392  | 1.19986e-05 |        0.0237391 |        0.0622291 |
| Chemotherapy_YES              |  0.0389446 |    1.03971  | 0.712578    |       -0.168251  |        0.24614   |
| Age at Diagnosis              |  0.0303407 |    1.03081  | 2.12911e-22 |        0.0242324 |        0.036449  |
| PR Status_Positive            | -0.0247282 |    0.975575 | 0.745715    |       -0.17418   |        0.124724  |

## Interpretation

- Kaplan-Meier curves compare survival probability across clinical groups.
- Log-rank tests evaluate whether survival differences between groups are statistically significant.
- Cox proportional hazards modeling provides interpretable hazard ratios.
- Random Survival Forests capture nonlinear survival patterns and provide model-based risk ranking.

## Limitations

- This project is for analytical and educational purposes only.
- Results should not be interpreted as clinical guidance.
- Survival models may be affected by missingness, censoring patterns, cohort bias, and proportional hazards assumptions.