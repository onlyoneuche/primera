"""Dataset checks usable before third-party packages have been installed."""
import csv
from collections import Counter
from io import StringIO

HEADERS = ["Timestamp", "Choose your gender", "Age", "What is your course?",
           "Your current year of Study", "What is your CGPA?", "Marital status",
           "Do you have Depression?", "Do you have Anxiety?", "Do you have Panic attack?",
           "Did you seek any specialist for a treatment?"]
YES_NO = HEADERS[6:]
CGPA = {"0-1.99", "2.00-2.49", "2.50-2.99", "3.00-3.49", "3.50-4.00"}


def require(condition, message):
    # Explicit exceptions are retained under python -O, unlike assert statements.
    if not condition:
        raise ValueError(message)


def validate_bytes(raw):
    reader = csv.reader(StringIO(raw.decode("utf-8-sig"), newline=""))
    lines = list(reader)
    require(bool(lines), "Dataset is empty.")
    headers = [v.strip() for v in lines[0]]
    require(len(set(headers)) == len(headers), "Duplicate CSV headers.")
    require(headers == HEADERS, "Dataset headers differ from the required 11-column source.")
    require(all(len(row) == 11 for row in lines[1:]), "Malformed CSV row.")
    records = [dict(zip(headers, (v.strip() for v in row))) for row in lines[1:]]
    require(len(records) == 101, "Expected exactly 101 survey responses.")
    require(Counter(r[HEADERS[7]] for r in records) == {"No": 66, "Yes": 35},
            "Expected depression target counts No=66, Yes=35.")
    require(sum(r["Age"] == "" for r in records) == 1, "Expected one missing age.")
    for r in records:
        require(r[HEADERS[1]] in {"Female", "Male"}, "Unexpected gender.")
        require(r[HEADERS[4]].lower() in {"year 1", "year 2", "year 3", "year 4"},
                "Unexpected year of study.")
        require(r[HEADERS[5]].replace(" ", "") in CGPA, "Unexpected CGPA band.")
        require(all(r[k] in {"Yes", "No"} for k in YES_NO), "Unexpected yes/no value.")
        require(bool(r["Timestamp"]) and bool(r[HEADERS[3]]), "Missing timestamp/course.")
        if r["Age"]:
            age = float(r["Age"])
            require(age.is_integer() and 18 <= age <= 24, "Age outside training range.")
    return records
