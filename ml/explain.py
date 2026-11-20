"""In-sample SHAP and held-out permutation summaries are reported separately."""
import numpy as np
import pandas as pd
import shap
from ml.config import SEED
from ml.pipelines import transformed_features, transformed_feature_names


def explain(pipeline, X, winner, output_dir):
    values = transformed_features(pipeline, X)
    names = transformed_feature_names(pipeline, list(X.columns))
    classifier = pipeline.named_steps["classifier"]
    np.random.seed(SEED)
    if winner in {"tree", "rf"}:
        explanation = shap.TreeExplainer(classifier).shap_values(values)
    else:
        background = shap.kmeans(values, 20)
        explainer = shap.KernelExplainer(lambda rows: classifier.predict_proba(rows)[:, 1], background)
        explanation = explainer.shap_values(values, nsamples=512, l1_reg=0.0, silent=True)
    if isinstance(explanation, list):
        explanation = explanation[1]
    explanation = np.asarray(explanation)
    if explanation.ndim == 3:
        explanation = explanation[:, :, 1]
    if explanation.shape != values.shape:
        raise ValueError(f"Unexpected SHAP shape {explanation.shape}; expected {values.shape}.")
    detailed = pd.DataFrame({"feature": names, "mean_abs_shap": np.abs(explanation).mean(axis=0)})
    detailed = detailed.sort_values("mean_abs_shap", ascending=False).reset_index(drop=True)
    detailed["rank"] = np.arange(1, len(detailed) + 1)
    detailed.to_csv(output_dir / "shap_mean_abs_detailed.csv", index=False)
    # Sum signed dummy contributions per row before measuring parent-feature magnitude.
    parents = list(dict.fromkeys(name.split("=")[0] for name in names))
    aggregated = np.column_stack([explanation[:, [i for i, n in enumerate(names) if n.split("=")[0] == p]].sum(axis=1)
                                  for p in parents])
    headline = pd.DataFrame({"feature": parents, "mean_abs_shap": np.abs(aggregated).mean(axis=0)})
    headline = headline.sort_values("mean_abs_shap", ascending=False).reset_index(drop=True)
    headline["rank"] = np.arange(1, len(headline) + 1)
    headline.to_csv(output_dir / "shap_mean_abs.csv", index=False)
    import matplotlib.pyplot as plt
    shap.summary_plot(explanation, values, feature_names=names, show=False, plot_size=(10, 7))
    plt.title("SHAP contributions on the full-data fit (in-sample)")
    plt.gcf().savefig(output_dir / "figures/shap_summary.png", dpi=200, bbox_inches="tight", facecolor="white")
    plt.close("all")
    return headline


def summarise_permutations(raw, winner):
    selected = raw.loc[raw.model == winner]
    # Average permutations within folds, then report variability across held-out folds.
    folds = selected.groupby(["repeat", "fold", "feature"])["f1_decrease"].mean().reset_index()
    summary = folds.groupby("feature")["f1_decrease"].agg(["mean", "std"]).reset_index()
    return summary.rename(columns={"mean": "f1_decrease_mean", "std": "f1_decrease_std"}).sort_values(
        "f1_decrease_mean", ascending=False)
