"""Regenerate the full research run without reducing the prespecified protocol."""
import argparse
from datetime import datetime, timezone
import hashlib
from importlib.metadata import distributions
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile
import time

# Bound native-library parallelism before numerical imports; grid workers are configurable.
for variable in ["OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"]:
    os.environ.setdefault(variable, "1")


def package_versions():
    return dict(sorted((d.metadata["Name"], d.version) for d in distributions() if d.metadata["Name"]))


def git_state(root):
    def git(*args):
        result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=False)
        return result.stdout.strip() if result.returncode == 0 else None
    return {"commit": git("rev-parse", "HEAD"), "branch": git("branch", "--show-current"),
            "dirty": bool(git("status", "--porcelain"))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs", type=int, default=1, help="Concurrent grid-search workers (default: 1).")
    args = parser.parse_args()
    if args.jobs < 1:
        parser.error("--jobs must be at least 1")
    from ml.config import ROOT, RAW, OUTPUTS, MODELS, SEED, FEATURES, MODEL_ORDER, THRESHOLD
    if not RAW.is_file():
        raise SystemExit("Original survey CSV missing. Run make data first. No results have been generated.")
    import joblib
    import numpy as np
    from ml.data import load_data, feature_target, course_table
    from ml.evaluate import evaluate, metric_summary, mean_confusions, outer_splits
    from ml.explain import explain, summarise_permutations
    from ml.pipelines import build_pipeline
    from ml.report import data_profile, create_figures, write_reports
    from ml.select_model import select_model, modal_parameters
    from ml.sensitivity import run_sensitivity
    from ml.course_mapping import FACULTIES
    started = time.perf_counter()
    np.random.seed(SEED)
    frame = load_data()
    X, y = feature_target(frame)
    grouping = course_table(frame)
    print("Course mapping for source review:\n" + grouping.to_string(index=False), flush=True)
    raw_checksum = hashlib.sha256(RAW.read_bytes()).hexdigest()
    git = git_state(ROOT)
    versions = package_versions()
    source_hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                     for folder in ["ml", "config", "scripts"] for p in sorted((ROOT / folder).rglob("*"))
                     if p.is_file() and "__pycache__" not in p.parts and p.suffix in {".py", ".json"}}
    (ROOT / "local").mkdir(exist_ok=True)
    # Publish only a successfully completed run. Previous results survive failures.
    with tempfile.TemporaryDirectory(prefix="research-", dir=ROOT / "local") as temporary:
        stage = Path(temporary)
        out, models = stage / "outputs", stage / "models"
        (out / "figures").mkdir(parents=True)
        models.mkdir()
        grouping.to_csv(out / "course_grouping.csv", index=False)
        phi = data_profile(frame, grouping, out)
        splits = outer_splits(X, y)
        folds, oof, importance = evaluate(X, y, splits, [*MODEL_ORDER, "dummy_most_frequent", "dummy_stratified"], jobs=args.jobs)
        summary, confusion = metric_summary(folds), mean_confusions(folds)
        folds.to_csv(out / "metrics_per_fold.csv", index=False)
        oof.to_csv(out / "out_of_fold_predictions.csv", index=False)
        importance.to_csv(out / "permutation_importance_per_fold.csv", index=False)
        summary.to_csv(out / "metrics_summary.csv", index=False)
        confusion.to_csv(out / "confusion_matrices.csv", index=False)
        selection = select_model(summary.to_dict("records"))
        winner = selection["winner"]
        print("Selected by the fixed rule:", winner, flush=True)
        sensitivity, sensitivity_folds = run_sensitivity(X, y, splits, winner, folds, args.jobs)
        sensitivity.to_csv(out / "sensitivity_analysis.csv", index=False)
        sensitivity_folds.to_csv(out / "sensitivity_per_fold.csv", index=False)
        parameters = modal_parameters(folds.to_dict("records"), winner)
        fitted = build_pipeline(winner).set_params(**parameters).fit(X, y)
        joblib.dump(fitted, models / "model.joblib")
        timestamp = datetime.now(timezone.utc).isoformat()
        retained = fitted.named_steps["faculty"].retained_groups_
        metadata = {"model_key": winner, "hyperparameters": parameters, "feature_order": FEATURES,
                    "feature_types": {f: ("continuous" if f == "age" else "ordinal" if f in {"year", "cgpa_band"}
                                          else "nominal" if f == "faculty_group" else "binary") for f in FEATURES},
                    "binary_encodings": {"gender": {"female": 0, "male": 1},
                                         "married_anxiety_panic_specialist": {"false": 0, "true": 1}},
                    "ordinal_encodings": {"year": [1, 2, 3, 4], "cgpa_band":
                                          {band: i for i, band in enumerate(["0-1.99", "2.00-2.49", "2.50-2.99", "3.00-3.49", "3.50-4.00"])}},
                    "faculty_groups": FACULTIES, "faculty_retained_groups": retained,
                    "faculty_merge_rule": "Counts below 5 merge into Other; fitted independently in each training fold",
                    "categories_seen": {f: sorted(X[f].dropna().unique().tolist()) for f in FEATURES if f != "age"},
                    "age_range": [int(X.age.min()), int(X.age.max())], "year_range": [int(X.year.min()), int(X.year.max())],
                    "training_date": timestamp, "git_commit": git["commit"], "git_dirty": git["dirty"],
                    "package_versions": versions, "seed": SEED, "threshold": THRESHOLD,
                    "cross_validated_scores": summary.set_index("model").loc[winner].to_dict(),
                    "cross_validated_prediction_rule": "estimator.predict; threshold_tradeoffs.csv reports probability thresholds",
                    "raw_csv_sha256": raw_checksum,
                    "model_sha256": hashlib.sha256((models / "model.joblib").read_bytes()).hexdigest()}
        (models / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
        print("Computing full-data SHAP explanations...", flush=True)
        shap_values = explain(fitted, X, winner, out)
        permutation = summarise_permutations(importance, winner)
        permutation.to_csv(out / "permutation_importance.csv", index=False)
        warnings = write_reports(frame, folds, summary, confusion, sensitivity, shap_values,
                                 permutation, selection, phi, oof, metadata, out)
        create_figures(frame, folds, summary, confusion, sensitivity, shap_values, permutation, out)
        if hashlib.sha256(RAW.read_bytes()).hexdigest() != raw_checksum:
            raise RuntimeError("Source data changed during training; refusing to publish results.")
        generated = sorted(str(p.relative_to(stage)) for p in stage.rglob("*") if p.is_file())
        manifest = {"git_commit": git["commit"], "git_branch": git["branch"], "git_dirty": git["dirty"],
                    "utc_timestamp": timestamp, "runtime_seconds": time.perf_counter() - started,
                    "seed": SEED, "python_version": platform.python_version(), "package_versions": versions,
                    "row_count": len(X), "class_counts": {str(k): int(v) for k, v in y.value_counts().items()},
                    "raw_csv_sha256": raw_checksum, "source_sha256": source_hashes,
                    "validation": {"outer_splits": 5, "outer_repeats": 10, "inner_splits": 3},
                    "files_generated": [*generated, "outputs/run_manifest.json"], "warnings": warnings}
        (out / "run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        for source, destination in [(out, OUTPUTS), (models, MODELS)]:
            destination.mkdir(exist_ok=True)
            for path in sorted(source.rglob("*")):
                if path.is_file() and path.name != "run_manifest.json":
                    target = destination / path.relative_to(source)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(path, target)
        shutil.copy2(out / "run_manifest.json", OUTPUTS / "run_manifest.json")
    print(summary.to_string(index=False), flush=True)
    print(f"Completed in {manifest['runtime_seconds']:.1f}s. Review outputs/RESULTS_SUMMARY.md before Phase 2.", flush=True)


if __name__ == "__main__":
    main()
