"""Small transparent grids with every learned operation inside the pipeline."""
import numpy as np
from imblearn.over_sampling import SMOTENC
from imblearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from ml.config import SEED, FEATURES
from ml.course_mapping import FACULTIES
from ml.features import RareFacultyGrouper


class SafeSMOTENC(SMOTENC):
    """Bound neighbours using only the training labels supplied to this fit."""
    def fit_resample(self, X, y, **params):
        _, counts = np.unique(y, return_counts=True)
        if len(counts) != 2 or counts.min() < 2:
            raise ValueError("SMOTENC requires at least two training examples of each class.")
        configured = self.k_neighbors
        self.k_neighbors = min(configured, int(counts.min()) - 1)
        try:
            return super().fit_resample(X, y, **params)
        finally:
            self.k_neighbors = configured


def estimator_grid(key):
    options = {
        "logreg": (LogisticRegression(max_iter=2000, solver="liblinear", random_state=SEED),
                   {"C": [0.01, 0.1, 1, 10], "penalty": ["l1", "l2"]}),
        "svm": (SVC(probability=True, random_state=SEED),
                {"C": [0.1, 1, 10], "kernel": ["linear", "rbf"], "gamma": ["scale"]}),
        "tree": (DecisionTreeClassifier(random_state=SEED),
                 {"max_depth": [2, 3, 4, 5, None], "min_samples_leaf": [1, 3, 5]}),
        "knn": (KNeighborsClassifier(), {"n_neighbors": [3, 5, 7, 9], "weights": ["uniform", "distance"]}),
        "rf": (RandomForestClassifier(n_estimators=300, random_state=SEED, n_jobs=1),
               {"max_depth": [3, 5, None], "min_samples_leaf": [1, 3]}),
    }
    estimator, grid = options[key]
    return estimator, {"classifier__" + name: values for name, values in grid.items()}


def build_pipeline(key, features=None):
    features = FEATURES if features is None else features
    # Fixed ordinal codes are vocabulary, not estimates learned from the held-out data.
    categorical = [f for f in features if f not in {"age", "faculty_group"}]
    pre = ColumnTransformer([
        ("age", SimpleImputer(strategy="median"), ["age"]),
        ("categorical", "passthrough", categorical),
        ("faculty", OrdinalEncoder(categories=[FACULTIES], dtype=float), ["faculty_group"]),
    ], sparse_threshold=0)
    faculty_index = 1 + len(categorical)
    encode = ColumnTransformer([
        ("values", "passthrough", list(range(faculty_index))),
        ("faculty", OneHotEncoder(handle_unknown="ignore", sparse_output=False), [faculty_index]),
    ], sparse_threshold=0)
    estimator, _ = estimator_grid(key)
    return Pipeline([
        ("faculty", RareFacultyGrouper()),
        ("preprocess", pre),
        ("smote", SafeSMOTENC(categorical_features=list(range(1, faculty_index + 1)),
                               random_state=SEED, k_neighbors=5)),
        ("encode", encode),
        ("scale", StandardScaler()),
        ("classifier", estimator),
    ])


def transformed_features(pipeline, X):
    """Classifier inputs for real rows: inference skips the training-only sampler."""
    prepared = pipeline.named_steps["faculty"].transform(X)
    prepared = pipeline.named_steps["preprocess"].transform(prepared)
    encoded = pipeline.named_steps["encode"].transform(prepared)
    return pipeline.named_steps["scale"].transform(encoded)


def transformed_feature_names(pipeline, features):
    categorical = [f for f in features if f not in {"age", "faculty_group"}]
    codes = pipeline.named_steps["encode"].named_transformers_["faculty"].categories_[0]
    return ["age", *categorical, *["faculty_group=" + FACULTIES[int(code)] for code in codes]]
