"""Real-data acceptance tests intentionally fail if the required CSV is absent."""
import numpy as np
import pytest
from ml.config import RAW, FEATURES
from ml.data import load_data, course_table
from ml.features import RareFacultyGrouper


@pytest.fixture(scope="module")
def data():
    return load_data()


def test_source_shape_and_target(data):
    assert len(data) == 101
    assert data.depression.value_counts().to_dict() == {0: 66, 1: 35}
    assert not data.columns.duplicated().any()


def test_allowed_values(data):
    assert data.age.isna().sum() == 1
    assert data.age.dropna().between(18, 24).all()
    assert set(data.year).issubset({1, 2, 3, 4})
    assert set(data.cgpa_band).issubset(set(range(5)))
    for key in ["gender", "married", "depression", "anxiety", "panic", "specialist"]:
        assert set(data[key]).issubset({0, 1})


def test_course_mapping_is_complete_and_auditable(data):
    mapped = course_table(data)
    assert set(mapped.raw_string) == set(data.raw_course)
    assert mapped.notna().all().all()
    assert mapped.loc[mapped.confidence == "low", "canonical_group"].eq("Other").all()


def test_final_rare_groups(data):
    transformer = RareFacultyGrouper().fit(data[FEATURES])
    counts = transformer.transform(data[FEATURES]).faculty_group.value_counts()
    # Other is the explicit fallback bucket and can itself be rare on a small fold.
    assert counts.drop("Other", errors="ignore").ge(5).all()


def test_missing_age_is_not_imputed_during_loading(data):
    assert np.isnan(data.loc[data.age.isna(), "age"]).all()
