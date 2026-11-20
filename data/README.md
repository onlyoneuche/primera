# Student Mental health source data

Required source: [Student Mental health by MD Shariful Islam](https://www.kaggle.com/datasets/shariful07/student-mental-health). The build spec identifies it as a 2020 Google Form survey from International Islamic University Malaysia, distributed under CC0.

Use `make data` to download the original archive. The source must have 101 rows, 11 columns, 66 No/35 Yes depression responses, and one missing age. The download command validates the CSV before writing it. Existing files are validated without modification. No substitute dataset or synthetic training data is permitted. The original was retrieved and validated on 20 November 2026; provenance and its SHA-256 are recorded in `source.json`.

`data/raw/Student_Mental_health.csv` is immutable. All cleaning occurs in code. Git attributes disable line-ending conversion for raw CSVs. The generated run manifest records a SHA-256 of the original bytes, and automated checks reject unexpected source shape or values.

| Raw field | Interpretation and cleaning |
| --- | --- |
| Timestamp | Submission timestamp; excluded from predictors |
| Choose your gender | Female=0, Male=1 |
| Age | Years; one expected missing value; in-fold median imputation |
| What is your course? | Free text; explicit canonical faculty mapping; unknown labels → Other, low confidence |
| Your current year of Study | Case-normalised year 1–4 |
| What is your CGPA? | Ordered 4.0-scale bands, mapped to 0–4 |
| Marital status | No=0, Yes=1; single/married meaning is an assumption |
| Do you have Depression? | Target: No=0, Yes=1; single self-report item |
| Do you have Anxiety? | Binary self-report predictor |
| Do you have Panic attack? | Binary self-report predictor |
| Did you seek any specialist for a treatment? | Binary prior-help predictor |

Expected issues include course typos/abbreviations, inconsistent year case, whitespace, rare faculties, and missing age. Actual observations belong in generated `outputs/data_profile.md` and `outputs/course_grouping.csv` after retrieval, not hand-entered results. Limitations and report inconsistencies are documented in `docs/DATA_NOTES.md`.
