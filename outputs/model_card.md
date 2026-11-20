# Model card

## Intended use

Research screening aid for university students; never a diagnosis or clinical triage service.

## Data and limitations

Single Malaysian institution; 101 survey responses from 2020. The target is a single self-reported yes/no item, not a validated clinical instrument. Training ages are 18–24 and study years 1–4. CGPA uses a 4.0 scale. Only female and male genders are represented. The positive class has 35 responses. Generalisation to Nigeria has not been validated. This is a screening result, not a diagnosis.

## Performance

| model   | accuracy      | precision     | recall        | f1            |
|:--------|:--------------|:--------------|:--------------|:--------------|
| logreg  | 0.726 ± 0.101 | 0.621 ± 0.224 | 0.597 ± 0.221 | 0.585 ± 0.183 |

## Explanations

| feature       |   mean_abs_shap |   rank |
|:--------------|----------------:|-------:|
| married       |           0.147 |      1 |
| anxiety       |           0.103 |      2 |
| faculty_group |           0.089 |      3 |
| gender        |           0.077 |      4 |
| year          |           0.058 |      5 |
| age           |           0.043 |      6 |
| cgpa_band     |           0.036 |      7 |
| specialist    |           0.029 |      8 |
| panic         |           0.013 |      9 |

| feature       |   f1_decrease_mean |   f1_decrease_std |
|:--------------|-------------------:|------------------:|
| married       |              0.213 |             0.123 |
| anxiety       |              0.020 |             0.069 |
| specialist    |              0.020 |             0.035 |
| gender        |              0.015 |             0.049 |
| age           |             -0.003 |             0.045 |
| panic         |             -0.003 |             0.033 |
| cgpa_band     |             -0.013 |             0.044 |
| faculty_group |             -0.016 |             0.073 |
| year          |             -0.019 |             0.058 |

## Deployment behaviour

Probability threshold 0.5. No student answers are retained. See threshold_tradeoffs.csv for threshold-based estimates.

## Ethical considerations and out-of-scope uses

Do not use for diagnosis, treatment decisions, admissions, discipline, insurance, or automated referrals. Higher risk should invite a supportive conversation. Lower risk must never discourage seeking support.

## Warnings

- Single Malaysian institution; 101 survey responses from 2020. The target is a single self-reported yes/no item, not a validated clinical instrument. Training ages are 18–24 and study years 1–4. CGPA uses a 4.0 scale. Only female and male genders are represented. The positive class has 35 responses. Generalisation to Nigeria has not been validated. This is a screening result, not a diagnosis.
- Folds and repetitions are dependent; mean ± SD is descriptive. No significance claims are made.
- SHAP uses an in-sample full-data fit. Permutation importance uses held-out folds. Neither establishes causation.
- Some F1 standard deviations are at least 0.150; model performance varies substantially across folds.
- Outer test folds contain as few as 7 positive examples.
- married has a strong descriptive target association (phi=0.596).
- Candidate mean-F1 differences are small relative to the highest-mean model's fold standard deviation.
- Estimator.predict differs from probability threshold 0.5 on 0 pooled selected-model predictions. Main CV/tuning metrics use estimator.predict; deployed inference uses probability ≥ 0.5. The threshold table separately estimates deployed behaviour. SVC may exhibit this difference.
