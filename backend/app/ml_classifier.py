from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
from sklearn.pipeline import Pipeline

from app.schemas import RiskLevel

BACKEND_ROOT = Path(__file__).resolve().parent.parent


class LogClassifier:
    def __init__(self, model_path: Path) -> None:
        if not model_path.exists():
            raise FileNotFoundError(
                f"Model not found at {model_path}. Run: python ml/train.py"
            )
        self._pipeline: Pipeline = joblib.load(model_path)
        self._classes = list(self._pipeline.named_steps["clf"].classes_)

    def predict(self, log_line: str) -> tuple[RiskLevel, float]:
        proba = self._pipeline.predict_proba([log_line])[0]
        idx = int(np.argmax(proba))
        label = self._classes[idx]
        confidence = float(proba[idx])
        return RiskLevel(label), confidence


_classifier: LogClassifier | None = None


def get_classifier(model_path: Path) -> LogClassifier:
    global _classifier
    if _classifier is None:
        _classifier = LogClassifier(model_path)
    return _classifier
