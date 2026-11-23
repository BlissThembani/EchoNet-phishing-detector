"""Loads the artefacts once and runs predictions for the API."""
import pickle
from pathlib import Path

import pandas as pd

ARTEFACTS_DIR = Path(__file__).resolve().parent.parent / "artefacts"

with open(ARTEFACTS_DIR / "model.p", "rb") as f:
    model = pickle.load(f)

with open(ARTEFACTS_DIR / "encoders.p", "rb") as f:
    encoders = pickle.load(f)

FEATURES = encoders["features"]
INVERSE_CLASS_MAP = encoders["inverse_class_map"]


def predict(records: list[dict]) -> list[dict]:
    """Returns label and phishing probability for each feature record."""
    X = pd.DataFrame(records)[FEATURES]
    labels = model.predict(X)
    phishing_col = list(model.classes_).index(1)
    probabilities = model.predict_proba(X)[:, phishing_col]
    return [
        {"prediction": INVERSE_CLASS_MAP[int(label)], "phishing_probability": round(float(p), 4)}
        for label, p in zip(labels, probabilities)
    ]
