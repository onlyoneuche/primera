"""Nested repeated CV; outer observations never participate in fitting/tuning."""
import json
import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.inspection import permutation_importance
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.model_selection import GridSearchCV, RepeatedStratifiedKFold, StratifiedKFold
from ml.config import SEED, N_SPLITS, N_REPEATS, INNER_SPLITS, THRESHOLD, METRICS
from ml.pipelines import build_pipeline, estimator_grid


def scores(y, predictions):
    return {"accuracy": accuracy_score(y, predictions),
            "precision": precision_score(y, predictions, zero_division=0),
            "recall": recall_score(y, predictions, zero_division=0),
            "f1": f1_score(y, predictions, zero_division=0)}


def threshold_f1(estimator, X, y):
    return f1_score(y, estimator.predict_proba(X)[:, 1] >= THRESHOLD, zero_division=0)


def outer_splits(X, y):
    cv = RepeatedStratifiedKFold(n_splits=N_SPLITS, n_repeats=N_REPEATS, random_state=SEED)
    return list(cv.split(X, y))


def tune(key, X, y, jobs=1):
    _, grid = estimator_grid(key)
    search = GridSearchCV(build_pipeline(key, list(X.columns)), grid, scoring="f1",
                          cv=StratifiedKFold(INNER_SPLITS, shuffle=True, random_state=SEED),
                          refit=True, n_jobs=jobs, error_score="raise")
    return search.fit(X, y)


def evaluate(X, y, splits, keys, *, jobs=1, importance=True):
    rows, predictions, importances = [], [], []
    for key in keys:
        for i, (train, test) in enumerate(splits):
            X_train, X_test, y_train, y_test = X.iloc[train], X.iloc[test], y.iloc[train], y.iloc[test]
            if key.startswith("dummy_"):
                strategy = "most_frequent" if key == "dummy_most_frequent" else "stratified"
                fitted = DummyClassifier(strategy=strategy, random_state=SEED).fit(X_train, y_train)
                best_params, synthetic, rare = {}, 0, []
            else:
                search = tune(key, X_train, y_train, jobs)
                fitted, best_params = search.best_estimator_, search.best_params_
                synthetic = int(sum(fitted.named_steps["smote"].sampling_strategy_.values()))
                rare = fitted.named_steps["faculty"].retained_groups_
            # Use estimator.predict for the specified accuracy/precision/recall/F1 comparison.
            # Store probabilities separately to audit the deployed 0.5 threshold and alternatives.
            predicted = fitted.predict(X_test)
            probability = fitted.predict_proba(X_test)[:, list(fitted.classes_).index(1)]
            tn, fp, fn, tp = confusion_matrix(y_test, predicted, labels=[0, 1]).ravel()
            repeat, fold = i // N_SPLITS + 1, i % N_SPLITS + 1
            rows.append({"model": key, "repeat": repeat, "fold": fold,
                         **scores(y_test, predicted), "tn": tn, "fp": fp, "fn": fn, "tp": tp,
                         "best_params": json.dumps(best_params, sort_keys=True),
                         "n_train": len(train), "n_test": len(test), "n_test_positive": int(y_test.sum()),
                         "n_synthetic": synthetic, "faculty_retained_groups": json.dumps(rare)})
            for index, actual, estimate, prob in zip(test, y_test, predicted, probability):
                predictions.append({"model": key, "repeat": repeat, "fold": fold, "row": int(index),
                                    "actual": int(actual), "predicted": int(estimate), "probability": float(prob)})
            if importance and not key.startswith("dummy_"):
                measured = permutation_importance(fitted, X_test, y_test, scoring="f1", n_repeats=20,
                                                  random_state=SEED, n_jobs=1)
                for feature, values in zip(X.columns, measured.importances):
                    for permutation, value in enumerate(values, 1):
                        importances.append({"model": key, "repeat": repeat, "fold": fold,
                                            "feature": feature, "permutation": permutation,
                                            "f1_decrease": float(value)})
            print(f"{key}: outer fold {i + 1}/{len(splits)} F1={rows[-1]['f1']:.3f}", flush=True)
    return pd.DataFrame(rows), pd.DataFrame(predictions), pd.DataFrame(importances)


def metric_summary(folds):
    result = folds.groupby("model")[METRICS].agg(["mean", "std"])
    result.columns = [f"{metric}_{stat}" for metric, stat in result.columns]
    return result.reset_index()


def mean_confusions(folds):
    counts = ["tn", "fp", "fn", "tp"]
    per_repeat = folds.groupby(["model", "repeat"])[counts].sum()
    return per_repeat.groupby("model").mean().reset_index()
