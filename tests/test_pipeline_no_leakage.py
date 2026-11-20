"""Fit spies inspect the actual data passed through nested training operations."""
import numpy as np
import pandas as pd
import pytest
from imblearn.pipeline import Pipeline
from sklearn.model_selection import StratifiedKFold
from ml.config import FEATURES
from ml.pipelines import build_pipeline, SafeSMOTENC
from ml.evaluate import tune, evaluate


@pytest.fixture
def sample():
    rng = np.random.default_rng(7)
    n = 60
    X = pd.DataFrame({"gender": rng.integers(0, 2, n), "age": np.arange(n, dtype=float) + 18,
                      "faculty_group": ["Health sciences"] * 30 + ["Law"] * 30,
                      "year": rng.integers(1, 5, n), "cgpa_band": rng.integers(0, 5, n),
                      "married": rng.integers(0, 2, n), "anxiety": rng.integers(0, 2, n),
                      "panic": rng.integers(0, 2, n), "specialist": rng.integers(0, 2, n)})[FEATURES]
    y = pd.Series([0] * 40 + [1] * 20)
    return X, y


def test_sampler_and_statistics_only_see_training_data(sample, monkeypatch):
    X, y = sample
    train, test = next(StratifiedKFold(3, shuffle=True, random_state=42).split(X, y))
    # An extreme held-out age makes leakage visible in learned statistics.
    X.loc[test, "age"] = 10000
    X.loc[train[0], "age"] = np.nan
    original = SafeSMOTENC.fit_resample
    seen = []

    def spy(self, values, labels, **params):
        seen.append(np.asarray(values).copy())
        assert len(values) == len(train)
        assert np.max(np.asarray(values)[:, 0]) < 10000
        return original(self, values, labels, **params)

    monkeypatch.setattr(SafeSMOTENC, "fit_resample", spy)
    model = build_pipeline("logreg")
    assert isinstance(model, Pipeline)
    model.fit(X.iloc[train], y.iloc[train])
    median = model.named_steps["preprocess"].named_transformers_["age"].statistics_[0]
    assert median == X.iloc[train].age.median()
    assert len(seen) == 1
    model.predict(X.iloc[test])
    assert len(seen) == 1  # inference cannot resample test observations


def test_every_inner_fit_is_a_subset_of_outer_training(sample, monkeypatch):
    import ml.features as features
    X, y = sample
    train, test = next(StratifiedKFold(3, shuffle=True, random_state=42).split(X, y))
    allowed = set(X.iloc[train].index)
    calls = []
    original = features.RareFacultyGrouper.fit

    def spy(self, rows, labels=None):
        calls.append(set(rows.index))
        assert set(rows.index) <= allowed
        assert not set(rows.index) & set(test)
        return original(self, rows, labels)

    monkeypatch.setattr(features.RareFacultyGrouper, "fit", spy)
    tune("logreg", X.iloc[train], y.iloc[train])
    assert len(calls) == 8 * 3 + 1
    assert calls[-1] == allowed  # outer-training refit after inner tuning
    assert all(len(indices) < len(allowed) for indices in calls[:-1])


def test_synthetic_categories_are_valid(sample, monkeypatch):
    X, y = sample
    original = SafeSMOTENC.fit_resample

    def spy(self, values, labels, **params):
        result, targets = original(self, values, labels, **params)
        for index in self.categorical_features:
            assert set(np.asarray(result)[:, index]) <= set(np.asarray(values)[:, index])
        return result, targets

    monkeypatch.setattr(SafeSMOTENC, "fit_resample", spy)
    build_pipeline("logreg").fit(X, y)


def test_rare_groups_are_fitted_without_test_counts(sample):
    X, y = sample
    X.loc[:3, "faculty_group"] = "Education"
    model = build_pipeline("tree").fit(X.iloc[:30], y.iloc[:30].where(y.iloc[:30].index % 3 != 0, 1))
    assert "Education" not in model.named_steps["faculty"].retained_groups_
    changed = X.iloc[30:].copy()
    changed["faculty_group"] = "Education"
    assert model.named_steps["faculty"].transform(changed).faculty_group.eq("Other").all()


def test_same_seed_reproduces_nested_metrics(sample):
    X, y = sample
    splits = list(StratifiedKFold(3, shuffle=True, random_state=42).split(X, y))
    first, predictions_a, _ = evaluate(X, y, splits, ["logreg"], importance=False)
    second, predictions_b, _ = evaluate(X, y, splits, ["logreg"], importance=False)
    pd.testing.assert_frame_equal(first, second)
    pd.testing.assert_frame_equal(predictions_a, predictions_b)
