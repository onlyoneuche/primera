"""Shared faculty mapping with train-fold-only estimation of rare categories."""
import json
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.utils.validation import check_is_fitted
from ml.config import MODELS
from ml.course_mapping import FACULTIES


def map_faculty(group_label, retained_groups=None):
    if group_label not in FACULTIES:
        raise ValueError("Unknown faculty group.")
    if retained_groups is None:
        metadata = json.loads((MODELS / "metadata.json").read_text())
        retained_groups = metadata["faculty_retained_groups"]
    return group_label if group_label in retained_groups else "Other"


class RareFacultyGrouper(TransformerMixin, BaseEstimator):
    def __init__(self, min_count=5):
        self.min_count = min_count

    def fit(self, X, y=None):
        counts = X["faculty_group"].value_counts()
        self.retained_groups_ = sorted(counts[counts >= self.min_count].index.tolist())
        self.feature_names_in_ = X.columns.to_numpy()
        self.n_features_in_ = X.shape[1]
        return self

    def transform(self, X):
        check_is_fitted(self, "retained_groups_")
        result = X.copy()
        result["faculty_group"] = result["faculty_group"].map(
            lambda value: map_faculty(value, self.retained_groups_))
        return result

    def get_feature_names_out(self, input_features=None):
        check_is_fitted(self, "feature_names_in_")
        return self.feature_names_in_
