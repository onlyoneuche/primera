"""Load one trusted research artifact; perform stateless category-only inference."""
import hashlib
import json
import joblib
import pandas as pd
from ml.config import FEATURES, MODELS, THRESHOLD
from ml.features import map_faculty
from ml.course_mapping import FACULTIES
from app.messages import COPY


class Predictor:
    def __init__(self):
        self.metadata = json.loads((MODELS / "metadata.json").read_text())
        path = MODELS / "model.joblib"
        if hashlib.sha256(path.read_bytes()).hexdigest() != self.metadata["model_sha256"]:
            raise RuntimeError("Model integrity check failed.")
        if (self.metadata["feature_order"] != FEATURES or
                self.metadata["faculty_groups"] != FACULTIES or
                self.metadata["threshold"] != THRESHOLD):
            raise RuntimeError("Model configuration does not match the application.")
        self.model = joblib.load(path)
        if self.model.named_steps["faculty"].retained_groups_ != self.metadata["faculty_retained_groups"]:
            raise RuntimeError("Faculty mapping does not match model metadata.")

    def features(self, answers):
        values = answers.model_dump()
        values["gender"] = self.metadata["binary_encodings"]["gender"][values["gender"]]
        values["cgpa_band"] = self.metadata["ordinal_encodings"]["cgpa_band"][values["cgpa_band"]]
        values["faculty_group"] = map_faculty(values["faculty_group"], self.metadata["faculty_retained_groups"])
        for field in ["married", "anxiety", "panic", "specialist"]:
            values[field] = int(values[field])
        return pd.DataFrame([values], columns=FEATURES)

    def predict(self, answers):
        # Answers/features/probabilities are local variables, never retained on the instance.
        index = list(self.model.classes_).index(1)
        probability = self.model.predict_proba(self.features(answers))[0, index]
        category = "higher" if probability >= THRESHOLD else "lower"
        notes = []
        if not self.metadata["age_range"][0] <= answers.age <= self.metadata["age_range"][1]:
            notes.append(COPY["out_of_range"]["age"])
        if answers.year == 4:
            notes.append(COPY["out_of_range"]["year"])
        return {"category": category, **COPY["results"][category],
                "disclaimer": COPY["disclaimer"], "out_of_range_notes": notes,
                "model_note": COPY["model_note"]}
