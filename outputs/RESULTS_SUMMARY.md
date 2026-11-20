# Results summary

All values below are generated from this run.

## Class balance

|   target |   count |
|---------:|--------:|
|    0.000 |  66.000 |
|    1.000 |  35.000 |

## Preprocessing

| operation             | detail                                                                                                                                                                                          |
|:----------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Age median imputation | One missing source value; median fitted in each training fold                                                                                                                                   |
| Course groups         | 49 original strings; 48 after whitespace stripping; final retained groups: Business and economics, Education, Engineering and computing, Health sciences, Humanities and social sciences, Other |
| Encoding              | Fixed binary/ordinal vocabularies; faculty one-hot encoding after in-fold SMOTENC                                                                                                               |
| Scaling               | StandardScaler fitted on each resampled training fold                                                                                                                                           |

| model   |   mean_synthetic_per_fold |
|:--------|--------------------------:|
| knn     |                    24.800 |
| logreg  |                    24.800 |
| rf      |                    24.800 |
| svm     |                    24.800 |
| tree    |                    24.800 |

## Model comparison

| model               | accuracy      | precision     | recall        | f1            |
|:--------------------|:--------------|:--------------|:--------------|:--------------|
| dummy_most_frequent | 0.653 ± 0.007 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| dummy_stratified    | 0.546 ± 0.107 | 0.320 ± 0.178 | 0.274 ± 0.152 | 0.295 ± 0.164 |
| knn                 | 0.663 ± 0.101 | 0.513 ± 0.139 | 0.563 ± 0.188 | 0.530 ± 0.152 |
| logreg              | 0.726 ± 0.101 | 0.621 ± 0.224 | 0.597 ± 0.221 | 0.585 ± 0.183 |
| rf                  | 0.759 ± 0.080 | 0.693 ± 0.168 | 0.617 ± 0.157 | 0.635 ± 0.123 |
| svm                 | 0.717 ± 0.097 | 0.616 ± 0.174 | 0.594 ± 0.197 | 0.583 ± 0.157 |
| tree                | 0.706 ± 0.105 | 0.591 ± 0.191 | 0.617 ± 0.179 | 0.588 ± 0.153 |

## Mean confusion matrices per repeat

| model               |     tn |     fp |     fn |     tp |
|:--------------------|-------:|-------:|-------:|-------:|
| dummy_most_frequent | 66.000 |  0.000 | 35.000 |  0.000 |
| dummy_stratified    | 45.600 | 20.400 | 25.400 |  9.600 |
| knn                 | 47.200 | 18.800 | 15.300 | 19.700 |
| logreg              | 52.400 | 13.600 | 14.100 | 20.900 |
| rf                  | 55.000 | 11.000 | 13.400 | 21.600 |
| svm                 | 51.600 | 14.400 | 14.200 | 20.800 |
| tree                | 49.700 | 16.300 | 13.400 | 21.600 |

Each student is tested exactly once per repeat; confusion counts are averaged over the ten repeats.

## Most frequently chosen parameters

| model   | modal_parameters                                                                     |
|:--------|:-------------------------------------------------------------------------------------|
| logreg  | {"classifier__C": 1, "classifier__penalty": "l2"}                                    |
| tree    | {"classifier__max_depth": 2, "classifier__min_samples_leaf": 1}                      |
| knn     | {"classifier__n_neighbors": 3, "classifier__weights": "distance"}                    |
| svm     | {"classifier__C": 0.1, "classifier__gamma": "scale", "classifier__kernel": "linear"} |
| rf      | {"classifier__max_depth": 3, "classifier__min_samples_leaf": 1}                      |

## Selection

Highest mean F1: rf, 0.635; SD=0.123.

Tie set (within that SD): logreg, tree, knn, svm, rf.

Fixed simplicity order: logreg, tree, knn, svm, rf.

Selected model: **logreg**.

Final parameters are the most frequent complete parameter combination across outer folds. Frequency ties use smaller values in alphabetical parameter-name order; unbounded depth sorts last; strings use lexical order.

## Sensitivity analysis

| subset                                | accuracy      | precision     | recall        | f1            |
|:--------------------------------------|:--------------|:--------------|:--------------|:--------------|
| all nine features                     | 0.726 ± 0.101 | 0.621 ± 0.224 | 0.597 ± 0.221 | 0.585 ± 0.183 |
| without anxiety and panic             | 0.749 ± 0.097 | 0.673 ± 0.268 | 0.577 ± 0.227 | 0.593 ± 0.200 |
| without specialist                    | 0.739 ± 0.082 | 0.684 ± 0.245 | 0.560 ± 0.223 | 0.577 ± 0.171 |
| without anxiety, panic and specialist | 0.736 ± 0.095 | 0.666 ± 0.275 | 0.537 ± 0.215 | 0.565 ± 0.193 |

all nine features: mean F1 0.585 (change +0.000 from the reference).

without anxiety and panic: mean F1 0.593 (change +0.008 from the reference).

without specialist: mean F1 0.577 (change -0.008 from the reference).

without anxiety, panic and specialist: mean F1 0.565 (change -0.020 from the reference).

## SHAP (in-sample)

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

## Held-out permutation importance

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

## Threshold trade-offs (pooled repeated out-of-fold predictions)

|   threshold |   accuracy |   precision |   recall |    f1 |
|------------:|-----------:|------------:|---------:|------:|
|       0.300 |      0.545 |       0.424 |    0.883 | 0.573 |
|       0.400 |      0.653 |       0.500 |    0.737 | 0.596 |
|       0.500 |      0.726 |       0.606 |    0.597 | 0.601 |
|       0.600 |      0.757 |       0.733 |    0.471 | 0.574 |

Each student contributes ten probabilities to this pooled descriptive table; these are not independent observations. The deployed threshold remains 0.5; this table does not change model selection.

## Warnings and caveats

- Single Malaysian institution; 101 survey responses from 2020. The target is a single self-reported yes/no item, not a validated clinical instrument. Training ages are 18–24 and study years 1–4. CGPA uses a 4.0 scale. Only female and male genders are represented. The positive class has 35 responses. Generalisation to Nigeria has not been validated. This is a screening result, not a diagnosis.
- Folds and repetitions are dependent; mean ± SD is descriptive. No significance claims are made.
- SHAP uses an in-sample full-data fit. Permutation importance uses held-out folds. Neither establishes causation.
- Some F1 standard deviations are at least 0.150; model performance varies substantially across folds.
- Outer test folds contain as few as 7 positive examples.
- married has a strong descriptive target association (phi=0.596).
- Candidate mean-F1 differences are small relative to the highest-mean model's fold standard deviation.
- Estimator.predict differs from probability threshold 0.5 on 0 pooled selected-model predictions. Main CV/tuning metrics use estimator.predict; deployed inference uses probability ≥ 0.5. The threshold table separately estimates deployed behaviour. SVC may exhibit this difference.
