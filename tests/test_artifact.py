import hashlib
import json
import joblib
import numpy as np
import pandas as pd
from ml.config import MODELS, FEATURES


def test_deployed_artifact_loads_and_predicts():
    path = MODELS / "model.joblib"
    assert path.is_file(), "Run make train to generate the real fitted artifact."
    metadata = json.loads((MODELS / "metadata.json").read_text())
    assert hashlib.sha256(path.read_bytes()).hexdigest() == metadata["model_sha256"]
    fitted = joblib.load(path)
    examples = pd.DataFrame([
        [0, 18, "Health sciences", 1, 0, 0, 0, 0, 0],
        [1, 24, "Engineering and computing", 4, 4, 1, 1, 1, 1],
        [0, 21, "Education", 2, 2, 0, 1, 0, 0],
    ], columns=FEATURES)
    probabilities = fitted.predict_proba(examples)
    assert probabilities.shape == (3, 2)
    assert np.isfinite(probabilities).all()
    assert ((probabilities >= 0) & (probabilities <= 1)).all()
    np.testing.assert_allclose(probabilities.sum(axis=1), 1)
    np.testing.assert_array_equal(fitted.predict(examples), fitted.predict(examples))
