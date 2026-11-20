"""Prespecified ablations reuse exactly the main run's outer splits."""
import pandas as pd
from ml.config import METRICS
from ml.evaluate import evaluate

SUBSETS = {
    "all nine features": [],
    "without anxiety and panic": ["anxiety", "panic"],
    "without specialist": ["specialist"],
    "without anxiety, panic and specialist": ["anxiety", "panic", "specialist"],
}


def run_sensitivity(X, y, splits, winner, main_folds, jobs=1):
    details = []
    for label, removed in SUBSETS.items():
        if removed:
            folds, _, _ = evaluate(X.drop(columns=removed), y, splits, [winner], jobs=jobs, importance=False)
        else:
            folds = main_folds.loc[main_folds.model == winner].copy()
        folds["subset"] = label
        details.append(folds)
    detail = pd.concat(details, ignore_index=True)
    summary = detail.groupby("subset", sort=False)[METRICS].agg(["mean", "std"])
    summary.columns = [f"{metric}_{stat}" for metric, stat in summary.columns]
    return summary.reset_index(), detail
