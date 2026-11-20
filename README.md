# Primera

Primera is a final-year software engineering research project with the aim **to develop a machine learning-based early-warning system for predicting depression risk among university students.**

The study compares logistic regression, support vector machines, decision trees, k-nearest neighbours, and random forests against two baselines using 101 survey responses from the [Student Mental health dataset on Kaggle](https://www.kaggle.com/datasets/shariful07/student-mental-health), collected at one Malaysian university. Repeated nested cross-validation separates model tuning from evaluation, with learned preprocessing and SMOTENC confined to training folds. Sensitivity analyses, SHAP, and held-out permutation importance examine the models' reliance on different inputs.

Random forest achieved the highest mean F1 (**0.635 ± 0.123**), while the pre-specified selection rule favoured the simpler logistic regression model (**0.585 ± 0.183**). The [research results](outputs/RESULTS_SUMMARY.md) document the full comparison, selection rationale, explanations, and limitations.

The selected model powers a nine-question web check-in that provides supportive screening results without saving answers. It does not provide a diagnosis. Findings are limited by the small, self-reported dataset; generalisation to Nigerian students remains unvalidated.

## Get started

Requires Docker, Compose v2, Make, and internet access.

```sh
make setup     # Build the development image
make data      # Fetch and validate the original survey
make train     # Generate results, explanations, and the model
make test      # Run checks against the data and fitted artifact
```

Run `make run`, then open http://127.0.0.1:8000. `make down` stops the local app.

## Commands

| Command | Purpose |
| --- | --- |
| `make check` | Dependency-free checks; host Python 3.9+ |
| `make verify` | Repeat the full research run twice; compare CSVs |
| `make docker` | Build the production image |
| `make run` / `make down` | Start / stop the local check-in app |

## Where things live

| Path | Contents |
| --- | --- |
| `ml/` | Training, evaluation, model selection, explanations |
| `outputs/` · `models/` | Generated research evidence and fitted artifacts; tracked |
| `local/` | Original documents and local working files; Git-ignored |

[Build spec](docs/BUILD_SPEC.md) · [Development](docs/DEVELOPMENT.md) · [Agent guide](AGENTS.md) · [Progress & blockers](docs/IMPLEMENTATION_STATUS.md)

101 survey responses from one Malaysian university; a single self-reported target. Generalisation to Nigeria is unvalidated. [Data & limitations](data/README.md).

[MIT](LICENSE) code · CC0 dataset
