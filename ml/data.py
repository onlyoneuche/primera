"""Read immutable source data and apply deterministic, non-statistical cleaning."""
import csv
import io
import pandas as pd
from ml.config import RAW, FEATURES, CGPA_BANDS
from ml.course_mapping import describe_course
from ml.validation import HEADERS, validate_bytes

NAMES = ["timestamp", "gender", "age", "course", "year", "cgpa_band",
         "married", "depression", "anxiety", "panic", "specialist"]


def load_data(path=RAW):
    if not path.is_file():
        raise FileNotFoundError("Original survey CSV missing. Run make data before training.")
    records = validate_bytes(path.read_bytes())
    frame = pd.DataFrame(records).rename(columns=dict(zip(HEADERS, NAMES)))
    # Preserve untrimmed labels for the audit table even though modelling uses stripped strings.
    raw_records = list(csv.reader(io.StringIO(path.read_text(encoding="utf-8-sig"), newline="")))
    course_index = [name.strip() for name in raw_records[0]].index("What is your course?")
    frame["raw_course"] = [row[course_index] for row in raw_records[1:]]
    frame["age"] = pd.to_numeric(frame["age"], errors="coerce")
    frame["gender"] = frame["gender"].map({"Female": 0, "Male": 1})
    for key in ["married", "depression", "anxiety", "panic", "specialist"]:
        frame[key] = frame[key].map({"No": 0, "Yes": 1})
    frame["year"] = frame["year"].str.lower().str.extract(r"([1-4])", expand=False).astype(int)
    frame["cgpa_label"] = frame["cgpa_band"].str.replace(" ", "", regex=False)
    frame["cgpa_band"] = frame["cgpa_label"].map(dict(zip(CGPA_BANDS, range(5))))
    frame["faculty_group"] = frame["course"].map(lambda value: describe_course(value)["canonical_group"])
    return frame


def feature_target(frame):
    return frame[FEATURES].copy(), frame["depression"].copy()


def course_table(frame):
    return pd.DataFrame([describe_course(value) for value in sorted(frame["raw_course"].unique())])
