"""
Train TF-IDF + Logistic Regression classifier for security log risk labels.

Usage (from repo root):
  python -m venv .venv && .venv\\Scripts\\activate
  pip install -r backend/requirements.txt
  python ml/train.py
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "sample_logs.csv"
MODEL_DIR = ROOT / "models"
MODEL_PATH = MODEL_DIR / "log_classifier.joblib"
METRICS_PATH = MODEL_DIR / "training_metrics.json"

LABELS = ["Benign", "Suspicious", "Malicious"]


def main() -> None:
    df = pd.read_csv(DATA_PATH)
    if df.empty or "log_line" not in df.columns or "label" not in df.columns:
        raise SystemExit(f"Invalid dataset at {DATA_PATH}")

    invalid = set(df["label"].unique()) - set(LABELS)
    if invalid:
        raise SystemExit(f"Unknown labels in dataset: {invalid}")

    X = df["log_line"].astype(str)
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    pipeline = Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    ngram_range=(1, 2),
                    min_df=1,
                    max_features=5000,
                    sublinear_tf=True,
                ),
            ),
            (
                "clf",
                LogisticRegression(
                    max_iter=1000,
                    class_weight="balanced",
                    random_state=42,
                ),
            ),
        ]
    )

    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)

    accuracy = float(accuracy_score(y_test, y_pred))
    f1_macro = float(f1_score(y_test, y_pred, average="macro"))
    report = classification_report(y_test, y_pred, output_dict=True)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)

    metrics = {
        "accuracy": accuracy,
        "f1_macro": f1_macro,
        "test_size": len(y_test),
        "train_size": len(y_train),
        "classification_report": report,
    }
    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print(f"Model saved to {MODEL_PATH}")
    print(f"Accuracy: {accuracy:.3f}  F1 (macro): {f1_macro:.3f}")
    print(classification_report(y_test, y_pred))


if __name__ == "__main__":
    main()
