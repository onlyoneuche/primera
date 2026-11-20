"""Fixed research settings; never tune these using test-fold results."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/Student_Mental_health.csv"
OUTPUTS = ROOT / "outputs"
MODELS = ROOT / "models"
SEED = 42
N_SPLITS = 5
N_REPEATS = 10
INNER_SPLITS = 3
THRESHOLD = 0.5
FEATURES = ["gender", "age", "faculty_group", "year", "cgpa_band",
            "married", "anxiety", "panic", "specialist"]
CGPA_BANDS = ["0-1.99", "2.00-2.49", "2.50-2.99", "3.00-3.49", "3.50-4.00"]
BINARY = ["gender", "married", "anxiety", "panic", "specialist"]
MODEL_ORDER = ["logreg", "tree", "knn", "svm", "rf"]
METRICS = ["accuracy", "precision", "recall", "f1"]
LIMITATIONS = (
    "Single Malaysian institution; 101 survey responses from 2020. "
    "The target is a single self-reported yes/no item, not a validated clinical instrument. "
    "Training ages are 18–24 and study years 1–4. CGPA uses a 4.0 scale. "
    "Only female and male genders are represented. The positive class has 35 responses. "
    "Generalisation to Nigeria has not been validated. This is a screening result, not a diagnosis."
)
