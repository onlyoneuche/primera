"""Generate every research table and figure from computed values."""
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from ml.config import FEATURES, METRICS, LIMITATIONS, MODEL_ORDER, SEED
from ml.course_mapping import FACULTIES
from ml.select_model import modal_parameters

COLORS = ["#0B7A5E", "#2468A0", "#8553A1", "#AD6100", "#4D6760", "#64748B", "#596A8A"]
plt.rcParams.update({"font.size": 12, "axes.titlesize": 15, "axes.labelsize": 12,
                     "figure.facecolor": "white", "savefig.facecolor": "white"})


def table(frame):
    return frame.to_markdown(index=False, floatfmt=".3f")


def metric_table(summary, first="model"):
    return table(pd.DataFrame({first: summary[first], **{
        metric: [f"{mean:.3f} ± {std:.3f}" for mean, std in
                 zip(summary[f"{metric}_mean"], summary[f"{metric}_std"])] for metric in METRICS}}))


def save_figure(fig, destination):
    fig.tight_layout()
    fig.savefig(destination, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def data_profile(frame, grouping, directory):
    binary = ["gender", "married", "anxiety", "panic", "specialist"]
    phi = {key: float(frame[key].corr(frame.depression)) for key in binary}
    sections = ["# Data profile", "\nTarget: 1 = self-reported depression; 0 = No.",
                table(frame.depression.value_counts().sort_index().rename_axis("target").reset_index(name="count")),
                "## Missingness after non-statistical cleaning",
                table(frame.isna().sum().rename_axis("column").reset_index(name="missing"))]
    for feature in [*FEATURES, "course"]:
        sections.extend([f"## {feature}",
                         table(frame[feature].value_counts(dropna=False).rename_axis(feature).reset_index(name="count")),
                         table(pd.crosstab(frame[feature].fillna("Missing"), frame.depression).reset_index())])
    sections += ["## Binary predictor correlations (phi)",
                 table(pd.DataFrame([{"feature": k, "phi": v} for k, v in phi.items()])),
                 "Strong associations are flagged at absolute phi ≥ 0.5; these are descriptive, not causal.",
                 "## Course mapping", table(grouping),
                 "Rare-group counts are learned independently in each training fold. "
                 "The mapping table describes canonical categories before rare-group merging.", LIMITATIONS]
    (directory / "data_profile.md").write_text("\n\n".join(sections) + "\n")
    return phi


def create_figures(frame, folds, summary, confusions, sensitivity, shap_values, permutations, directory):
    figures = directory / "figures"
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(["No (0)", "Yes (1)"], frame.depression.value_counts().reindex([0, 1]), color=COLORS[:2])
    ax.set(title="Self-reported depression class balance", xlabel="Survey response", ylabel="Students")
    save_figure(fig, figures / "class_balance.png")

    fig, ax = plt.subplots(figsize=(13, 6))
    locations = np.arange(len(summary))
    for i, metric in enumerate(METRICS):
        ax.bar(locations + (i - 1.5) * 0.2, summary[f"{metric}_mean"], width=0.19,
               yerr=summary[f"{metric}_std"], capsize=3, label=metric, color=COLORS[i])
    ax.set_xticks(locations, summary.model, rotation=20, ha="right")
    ax.set(title="Repeated nested CV: mean ± standard deviation", xlabel="Model", ylabel="Metric value", ylim=(0, 1.25))
    ax.legend(ncols=4)
    save_figure(fig, figures / "metric_comparison.png")

    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    for ax, row in zip(axes.flat, confusions.itertuples()):
        matrix = np.array([[row.tn, row.fp], [row.fn, row.tp]])
        ax.imshow(matrix, cmap="Blues", vmin=0, vmax=101)
        for (r, c), value in np.ndenumerate(matrix):
            ax.text(c, r, f"{value:.3f}", ha="center", va="center", color="#17324D")
        ax.set(title=row.model, xlabel="Predicted class", ylabel="Actual class")
        ax.set_xticks([0, 1], ["No", "Yes"])
        ax.set_yticks([0, 1], ["No", "Yes"])
    for ax in axes.flat[len(confusions):]:
        ax.set_visible(False)
    fig.suptitle("Mean confusion counts per repeat (each student tested once per repeat)")
    save_figure(fig, figures / "confusion_matrices.png")

    fig, ax = plt.subplots(figsize=(12, 6))
    keys = summary.model.tolist()
    ax.boxplot([folds.loc[folds.model == key, "f1"] for key in keys], labels=keys)
    rng = np.random.default_rng(SEED)
    for i, key in enumerate(keys, 1):
        vals = folds.loc[folds.model == key, "f1"]
        ax.scatter(rng.normal(i, 0.04, len(vals)), vals, s=12, alpha=0.6, color=COLORS[(i - 1) % len(COLORS)])
    ax.set(title="F1 variability over 50 held-out folds", xlabel="Model", ylabel="Positive-class F1", ylim=(-0.02, 1.02))
    ax.tick_params(axis="x", rotation=20)
    save_figure(fig, figures / "fold_variability.png")

    for name, data, value, error, title, label in [
        ("shap_bar", shap_values, "mean_abs_shap", None, "SHAP on the full-data fit (in-sample)", "Mean absolute SHAP contribution"),
        ("permutation_importance", permutations, "f1_decrease_mean", "f1_decrease_std",
         "Permutation importance on held-out folds", "Mean decrease in F1 ± fold SD")]:
        ordered = data.sort_values(value)
        fig, ax = plt.subplots(figsize=(10, 7))
        ax.barh(ordered.feature, ordered[value], xerr=None if error is None else ordered[error], color=COLORS[0])
        ax.axvline(0, color="#17324D", linewidth=0.8)
        ax.set(title=title, xlabel=label, ylabel="Original input feature")
        save_figure(fig, figures / f"{name}.png")

    fig, ax = plt.subplots(figsize=(11, 6))
    ax.barh(sensitivity.subset, sensitivity.f1_mean, xerr=sensitivity.f1_std, color=COLORS[1], capsize=4)
    ax.invert_yaxis()
    ax.set(title="Selected-model sensitivity analysis", xlabel="Positive-class F1: mean ± SD", ylabel="Feature subset", xlim=(0, 1.2))
    save_figure(fig, figures / "sensitivity.png")


def write_reports(frame, folds, summary, confusions, sensitivity, shap_values, permutations,
                  selection, phi, oof, metadata, directory):
    winner = selection["winner"]
    best = selection["highest_mean_model"]
    baseline = float(summary.set_index("model").loc["dummy_most_frequent", "f1_mean"])
    warnings = [LIMITATIONS,
                "Folds and repetitions are dependent; mean ± SD is descriptive. No significance claims are made.",
                "SHAP uses an in-sample full-data fit. Permutation importance uses held-out folds. Neither establishes causation."]
    if selection["highest_mean_f1"] <= baseline:
        warnings.append("WARNING: The highest-mean candidate does not beat the majority-class baseline on F1.")
    if (summary.f1_std >= 0.15).any():
        warnings.append("Some F1 standard deviations are at least 0.150; model performance varies substantially across folds.")
    if int(folds.n_test_positive.min()) < 10:
        warnings.append(f"Outer test folds contain as few as {int(folds.n_test_positive.min())} positive examples.")
    for key, value in phi.items():
        if abs(value) >= 0.5:
            warnings.append(f"{key} has a strong descriptive target association (phi={value:.3f}).")
    if selection["highest_mean_std"] >= max(
            selection["highest_mean_f1"] - float(v) for v in summary.loc[summary.model.isin(MODEL_ORDER), "f1_mean"]):
        warnings.append("Candidate mean-F1 differences are small relative to the highest-mean model's fold standard deviation.")
    params = pd.DataFrame([{"model": key, "modal_parameters": json.dumps(modal_parameters(folds.to_dict("records"), key), sort_keys=True)}
                           for key in MODEL_ORDER])
    reasoning = ["# Model selection", metric_table(summary),
                 f"Highest mean F1: {best}, {selection['highest_mean_f1']:.3f}; SD={selection['highest_mean_std']:.3f}.",
                 "Tie set (within that SD): " + ", ".join(selection["tie_set"]) + ".",
                 "Fixed simplicity order: logreg, tree, knn, svm, rf.", f"Selected model: **{winner}**.",
                 "Final parameters are the most frequent complete parameter combination across outer folds. "
                 "Frequency ties use smaller values in alphabetical parameter-name order; unbounded depth sorts last; strings use lexical order.",
                 table(params), "\n".join(f"- {warning}" for warning in warnings)]
    (directory / "model_selection.md").write_text("\n\n".join(reasoning) + "\n")
    selected_oof = oof.loc[oof.model == winner]
    from ml.evaluate import scores
    thresholds = pd.DataFrame([{"threshold": t, **scores(selected_oof.actual, selected_oof.probability >= t)}
                               for t in [0.3, 0.4, 0.5, 0.6]])
    thresholds.to_csv(directory / "threshold_tradeoffs.csv", index=False)
    mismatch = int((selected_oof.predicted.to_numpy() != (selected_oof.probability >= 0.5).to_numpy()).sum())
    warnings.append(f"Estimator.predict differs from probability threshold 0.5 on {mismatch} pooled selected-model predictions. "
                    "Main CV/tuning metrics use estimator.predict; deployed inference uses probability ≥ 0.5. "
                    "The threshold table separately estimates deployed behaviour. SVC may exhibit this difference.")
    reference = float(sensitivity.iloc[0].f1_mean)
    descriptions = [f"{row.subset}: mean F1 {row.f1_mean:.3f} (change {row.f1_mean - reference:+.3f} from the reference)."
                    for row in sensitivity.itertuples()]
    retained = metadata["faculty_retained_groups"]
    preprocessing = pd.DataFrame([
        {"operation": "Age median imputation", "detail": "One missing source value; median fitted in each training fold"},
        {"operation": "Course groups", "detail": f"{frame.raw_course.nunique()} original strings; {frame.course.nunique()} after whitespace stripping; final retained groups: {', '.join(retained)}"},
        {"operation": "Encoding", "detail": "Fixed binary/ordinal vocabularies; faculty one-hot encoding after in-fold SMOTENC"},
        {"operation": "Scaling", "detail": "StandardScaler fitted on each resampled training fold"},
    ])
    synthetic = folds.loc[folds.model.isin(MODEL_ORDER)].groupby("model").n_synthetic.mean().reset_index(name="mean_synthetic_per_fold")
    summary_text = ["# Results summary", "All values below are generated from this run.",
                    "## Class balance", table(frame.depression.value_counts().sort_index().rename_axis("target").reset_index(name="count")),
                    "## Preprocessing", table(preprocessing), table(synthetic),
                    "## Model comparison", metric_table(summary), "## Mean confusion matrices per repeat", table(confusions),
                    "Each student is tested exactly once per repeat; confusion counts are averaged over the ten repeats.",
                    "## Most frequently chosen parameters", table(params),
                    "## Selection", "\n\n".join(reasoning[2:7]),
                    "## Sensitivity analysis", metric_table(sensitivity, "subset"), *descriptions,
                    "## SHAP (in-sample)", table(shap_values), "## Held-out permutation importance", table(permutations),
                    "## Threshold trade-offs (pooled repeated out-of-fold predictions)", table(thresholds),
                    "Each student contributes ten probabilities to this pooled descriptive table; these are not independent observations. "
                    "The deployed threshold remains 0.5; this table does not change model selection.",
                    "## Warnings and caveats", "\n".join(f"- {warning}" for warning in warnings)]
    (directory / "RESULTS_SUMMARY.md").write_text("\n\n".join(summary_text) + "\n")
    winner_scores = summary.loc[summary.model == winner]
    card = ["# Model card", "## Intended use", "Research screening aid for university students; never a diagnosis or clinical triage service.",
            "## Data and limitations", LIMITATIONS, "## Performance", metric_table(winner_scores),
            "## Explanations", table(shap_values), table(permutations),
            "## Deployment behaviour", "Probability threshold 0.5. No student answers are retained. See threshold_tradeoffs.csv for threshold-based estimates.",
            "## Ethical considerations and out-of-scope uses",
            "Do not use for diagnosis, treatment decisions, admissions, discipline, insurance, or automated referrals. "
            "Higher risk should invite a supportive conversation. Lower risk must never discourage seeking support.",
            "## Warnings", "\n".join(f"- {warning}" for warning in warnings)]
    (directory / "model_card.md").write_text("\n\n".join(card) + "\n")
    return warnings
