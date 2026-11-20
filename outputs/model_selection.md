# Model selection

| model               | accuracy      | precision     | recall        | f1            |
|:--------------------|:--------------|:--------------|:--------------|:--------------|
| dummy_most_frequent | 0.653 ± 0.007 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| dummy_stratified    | 0.546 ± 0.107 | 0.320 ± 0.178 | 0.274 ± 0.152 | 0.295 ± 0.164 |
| knn                 | 0.663 ± 0.101 | 0.513 ± 0.139 | 0.563 ± 0.188 | 0.530 ± 0.152 |
| logreg              | 0.726 ± 0.101 | 0.621 ± 0.224 | 0.597 ± 0.221 | 0.585 ± 0.183 |
| rf                  | 0.759 ± 0.080 | 0.693 ± 0.168 | 0.617 ± 0.157 | 0.635 ± 0.123 |
| svm                 | 0.717 ± 0.097 | 0.616 ± 0.174 | 0.594 ± 0.197 | 0.583 ± 0.157 |
| tree                | 0.706 ± 0.105 | 0.591 ± 0.191 | 0.617 ± 0.179 | 0.588 ± 0.153 |

Highest mean F1: rf, 0.635; SD=0.123.

Tie set (within that SD): logreg, tree, knn, svm, rf.

Fixed simplicity order: logreg, tree, knn, svm, rf.

Selected model: **logreg**.

Final parameters are the most frequent complete parameter combination across outer folds. Frequency ties use smaller values in alphabetical parameter-name order; unbounded depth sorts last; strings use lexical order.

| model   | modal_parameters                                                                     |
|:--------|:-------------------------------------------------------------------------------------|
| logreg  | {"classifier__C": 1, "classifier__penalty": "l2"}                                    |
| tree    | {"classifier__max_depth": 2, "classifier__min_samples_leaf": 1}                      |
| knn     | {"classifier__n_neighbors": 3, "classifier__weights": "distance"}                    |
| svm     | {"classifier__C": 0.1, "classifier__gamma": "scale", "classifier__kernel": "linear"} |
| rf      | {"classifier__max_depth": 3, "classifier__min_samples_leaf": 1}                      |

- Single Malaysian institution; 101 survey responses from 2020. The target is a single self-reported yes/no item, not a validated clinical instrument. Training ages are 18–24 and study years 1–4. CGPA uses a 4.0 scale. Only female and male genders are represented. The positive class has 35 responses. Generalisation to Nigeria has not been validated. This is a screening result, not a diagnosis.
- Folds and repetitions are dependent; mean ± SD is descriptive. No significance claims are made.
- SHAP uses an in-sample full-data fit. Permutation importance uses held-out folds. Neither establishes causation.
- Some F1 standard deviations are at least 0.150; model performance varies substantially across folds.
- Outer test folds contain as few as 7 positive examples.
- married has a strong descriptive target association (phi=0.596).
- Candidate mean-F1 differences are small relative to the highest-mean model's fold standard deviation.
