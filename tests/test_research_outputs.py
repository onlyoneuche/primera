"""Acceptance checks against the real completed protocol, never synthetic results."""
import hashlib
import json

import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

from ml.config import MODEL_ORDER, OUTPUTS, RAW


@pytest.fixture(scope="module")
def evidence():
    assert (OUTPUTS / "run_manifest.json").is_file(), "Run make train first."
    return (pd.read_csv(OUTPUTS / "metrics_per_fold.csv"),
            pd.read_csv(OUTPUTS / "out_of_fold_predictions.csv"))


def test_complete_protocol_and_shared_held_out_rows(evidence):
    folds, predictions = evidence
    keys = {*MODEL_ORDER, "dummy_most_frequent", "dummy_stratified"}
    assert set(folds.model) == set(predictions.model) == keys
    assert len(folds) == 350
    assert not folds.duplicated(["model", "repeat", "fold"]).any()
    assert set(folds.repeat) == set(range(1, 11))
    assert set(folds.fold) == set(range(1, 6))
    assert (folds.n_train + folds.n_test).eq(101).all()
    for (_, _), rows in predictions.groupby(["model", "repeat"]):
        assert len(rows) == 101
        assert set(rows.row) == set(range(101))
    # Every model must evaluate exactly the same students in each test fold.
    for (_, _), rows in predictions.groupby(["repeat", "fold"]):
        groups = list(rows.groupby("model"))
        reference = groups[0][1].sort_values("row")[["row", "actual"]].reset_index(drop=True)
        for _, model_rows in groups[1:]:
            pd.testing.assert_frame_equal(
                reference, model_rows.sort_values("row")[["row", "actual"]].reset_index(drop=True))


def test_reported_metrics_match_saved_predictions(evidence):
    folds, predictions = evidence
    scorers = {"accuracy": accuracy_score, "precision": precision_score,
               "recall": recall_score, "f1": f1_score}
    indexed = folds.set_index(["model", "repeat", "fold"])
    for key, rows in predictions.groupby(["model", "repeat", "fold"]):
        assert len(rows) == indexed.loc[key, "n_test"]
        assert rows.actual.sum() == indexed.loc[key, "n_test_positive"]
        for metric, scorer in scorers.items():
            options = {} if metric == "accuracy" else {"zero_division": 0}
            np.testing.assert_allclose(indexed.loc[key, metric],
                                       scorer(rows.actual, rows.predicted, **options), atol=1e-14)


def test_manifest_and_ablations_are_complete(evidence):
    manifest = json.loads((OUTPUTS / "run_manifest.json").read_text())
    assert manifest["raw_csv_sha256"] == hashlib.sha256(RAW.read_bytes()).hexdigest()
    assert manifest["validation"] == {"outer_splits": 5, "outer_repeats": 10, "inner_splits": 3}
    assert manifest["seed"] == 42
    for relative in manifest["files_generated"]:
        assert (OUTPUTS.parent / relative).is_file(), relative
    sensitivity = pd.read_csv(OUTPUTS / "sensitivity_per_fold.csv")
    assert sensitivity.groupby("subset").size().tolist() == [50] * 4
    assert not sensitivity.duplicated(["subset", "repeat", "fold"]).any()
