"""The selection rule is fixed before observing any results."""
import json
import math
from collections import Counter
from ml.config import MODEL_ORDER


def select_model(summary):
    indexed = {row["model"]: row for row in summary}
    if not all(key in indexed for key in MODEL_ORDER):
        raise ValueError("All five candidate models are required for selection.")
    for key in MODEL_ORDER:
        mean, std = indexed[key]["f1_mean"], indexed[key]["f1_std"]
        if not math.isfinite(mean) or not math.isfinite(std) or not 0 <= mean <= 1 or std < 0:
            raise ValueError("Selection requires finite F1 means and non-negative standard deviations.")
    # Fixed ordering also resolves identical maximum means deterministically.
    best = max(MODEL_ORDER, key=lambda key: indexed[key]["f1_mean"])
    mean = float(indexed[best]["f1_mean"])
    std = float(indexed[best]["f1_std"])
    tied = [key for key in MODEL_ORDER if mean - float(indexed[key]["f1_mean"]) <= std + 1e-12]
    return {"highest_mean_model": best, "highest_mean_f1": mean, "highest_mean_std": std,
            "tie_set": tied, "winner": tied[0]}


def parameter_order(params):
    # None represents unbounded tree depth and sorts after finite depths.
    def value_order(value):
        if value is None:
            return (2, 0)
        if isinstance(value, (int, float)):
            return (0, value)
        return (1, str(value))
    return tuple(value_order(value) for _, value in sorted(params.items()))


def modal_parameters(folds, key):
    candidates = [json.loads(row["best_params"]) for row in folds if row["model"] == key]
    if not candidates:
        raise ValueError(f"No outer-fold parameters recorded for {key}.")
    counts = Counter(json.dumps(value, sort_keys=True) for value in candidates)
    maximum = max(counts.values())
    tied = [json.loads(value) for value, count in counts.items() if count == maximum]
    return min(tied, key=parameter_order)
