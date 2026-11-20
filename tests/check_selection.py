"""Exercise the actual model-selection policy without numerical dependencies."""
import json
import unittest
from ml.config import MODEL_ORDER
from ml.select_model import select_model, modal_parameters


def summary(means, deviations):
    return [{"model": key, "f1_mean": mean, "f1_std": std}
            for key, mean, std in zip(MODEL_ORDER, means, deviations)]


class SelectionTests(unittest.TestCase):
    def test_simplicity_within_best_sd(self):
        result = select_model(summary([0.61, 0.65, 0.68, 0.70, 0.72], [0.01, 0.01, 0.02, 0.03, 0.12]))
        self.assertEqual(result["highest_mean_model"], "rf")
        self.assertEqual(result["winner"], "logreg")

    def test_uses_best_sd_not_each_candidates_sd(self):
        result = select_model(summary([0.1, 0.2, 0.3, 0.6, 0.8], [0.9, 0.9, 0.9, 0.9, 0.05]))
        self.assertEqual(result["winner"], "rf")

    def test_boundary_is_inclusive(self):
        result = select_model(summary([0.6, 0.5, 0.5, 0.5, 0.7], [0.1] * 5))
        self.assertEqual(result["winner"], "logreg")

    def test_zero_sd_and_identical_means(self):
        result = select_model(summary([0.5] * 5, [0] * 5))
        self.assertEqual(result["winner"], "logreg")
        self.assertEqual(result["tie_set"], MODEL_ORDER)

    def test_baselines_cannot_be_selected(self):
        rows = summary([0.1] * 5, [0] * 5)
        rows.append({"model": "dummy_stratified", "f1_mean": 0.9, "f1_std": 0.8})
        self.assertEqual(select_model(rows)["winner"], "logreg")

    def test_missing_candidate_rejected(self):
        with self.assertRaises(ValueError):
            select_model(summary([0.1] * 4, [0.1] * 4))

    def test_nan_scores_rejected(self):
        with self.assertRaises(ValueError):
            select_model(summary([float("nan")] * 5, [0.1] * 5))

    def test_parameter_mode_and_numeric_tie_break(self):
        combos = [{"classifier__C": 10, "classifier__penalty": "l1"},
                  {"classifier__C": 2, "classifier__penalty": "l2"}]
        rows = [{"model": "logreg", "best_params": json.dumps(p)} for p in combos]
        self.assertEqual(modal_parameters(rows, "logreg"), combos[1])
        rows.append(rows[0])
        self.assertEqual(modal_parameters(rows, "logreg"), combos[0])

    def test_finite_depth_sorts_before_unbounded(self):
        rows = [{"model": "tree", "best_params": json.dumps({"classifier__max_depth": d})} for d in [None, 3]]
        self.assertEqual(modal_parameters(rows, "tree"), {"classifier__max_depth": 3})


if __name__ == "__main__":
    unittest.main()
