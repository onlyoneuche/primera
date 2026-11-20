"""Standard-library checks for source integrity and strict data rejection.

These do not substitute for the real-data, leakage, and integration pytest suite.
"""
import ast
import csv
import hashlib
import io
from pathlib import Path
import subprocess
import unittest
from ml.config import ROOT
from ml.validation import HEADERS, validate_bytes
from ml.course_mapping import describe_course


def synthetic_csv():
    # Synthetic fixtures are only for validation tests; never training or research outputs.
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer)
    writer.writerow(HEADERS)
    for i in range(101):
        writer.writerow(["2020-01-01", "Female", "" if i == 0 else "21", "Engineering", "year 1",
                         "3.00 - 3.49", "No", "Yes" if i < 35 else "No", "No", "No", "No"])
    return buffer.getvalue().encode()


class FoundationTests(unittest.TestCase):
    def test_all_python_sources_parse(self):
        for folder in ["ml", "scripts", "tests"]:
            for path in (ROOT / folder).rglob("*.py"):
                with self.subTest(path=str(path.relative_to(ROOT))):
                    ast.parse(path.read_text(), filename=str(path))

    def test_local_storage_is_ignored(self):
        result = subprocess.run(["git", "check-ignore", "local/BUILD_SPEC.md", "local/example.csv"],
                                cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(result.stdout.splitlines()), 2)
        tracked = subprocess.run(["git", "ls-files", "local"], cwd=ROOT, text=True, capture_output=True, check=True)
        self.assertEqual(tracked.stdout, "")

    def test_research_outputs_are_not_ignored(self):
        result = subprocess.run(["git", "check-ignore", "outputs/metrics_summary.csv", "models/model.joblib"],
                                cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(result.returncode, 1)

    def test_valid_fixture(self):
        records = validate_bytes(synthetic_csv())
        self.assertEqual(len(records), 101)

    def test_wrong_shape_rejected(self):
        with self.assertRaisesRegex(ValueError, "101"):
            validate_bytes(b"\n".join(synthetic_csv().splitlines()[:-1]))

    def test_duplicate_headers_rejected(self):
        raw = synthetic_csv().replace(b"Timestamp", b"Age", 1)
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            validate_bytes(raw)

    def test_changed_target_counts_rejected(self):
        raw = synthetic_csv().replace(b",No,Yes,No,No,No", b",No,No,No,No,No", 1)
        with self.assertRaisesRegex(ValueError, "target counts"):
            validate_bytes(raw)

    def test_out_of_range_age_rejected(self):
        with self.assertRaisesRegex(ValueError, "Age"):
            validate_bytes(synthetic_csv().replace(b",21,Engineering", b",25,Engineering", 1))

    def test_malformed_row_rejected(self):
        with self.assertRaisesRegex(ValueError, "Malformed"):
            validate_bytes(synthetic_csv().replace(b",year 1,", b",year 1,extra,", 1))

    def test_nonbinary_value_rejected(self):
        with self.assertRaisesRegex(ValueError, "yes/no"):
            validate_bytes(synthetic_csv().replace(b",No,Yes,No,No,No", b",Maybe,Yes,No,No,No", 1))

    def test_unknown_course_is_explicitly_low_confidence(self):
        row = describe_course(" Unresolved department ")
        self.assertEqual(row["canonical_group"], "Other")
        self.assertEqual(row["confidence"], "low")

    def test_literal_course_normalisation(self):
        self.assertEqual(describe_course("  BIOMEDICAL   science ")["canonical_group"], "Health sciences")


if __name__ == "__main__":
    unittest.main()
