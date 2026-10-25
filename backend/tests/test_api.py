import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Ensure model exists before importing app
REPO_ROOT = Path(__file__).resolve().parents[2]
MODEL = REPO_ROOT / "ml" / "models" / "log_classifier.joblib"
if not MODEL.exists():
    pytest.skip("Train model first: python ml/train.py", allow_module_level=True)

os.environ.setdefault("API_KEY", "test-key")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("MODEL_PATH", str(MODEL))

from app.main import app  # noqa: E402

client = TestClient(app)
HEADERS = {"X-API-Key": "test-key"}


def test_health():
    r = client.get("/health")
    assert r.status_code == 200


def test_create_and_get_event():
    payload = {
        "raw_log": "2024-01-15 ids CRITICAL C2 beacon outbound 10.0.0.44 -> 185.220.101.42",
        "source": "ids",
    }
    r = client.post("/events", json=payload, headers=HEADERS)
    assert r.status_code == 201
    data = r.json()
    assert len(data) == 1
    assert data[0]["risk_level"] in ("Benign", "Suspicious", "Malicious")
    assert 0 <= data[0]["confidence"] <= 1

    event_id = data[0]["id"]
    r2 = client.get(f"/events/{event_id}")
    assert r2.status_code == 200

    r3 = client.patch(f"/events/{event_id}", json={"status": "Reviewed"}, headers=HEADERS)
    assert r3.status_code == 200
    assert r3.json()["status"] == "Reviewed"


def test_post_requires_api_key():
    r = client.post("/events", json={"raw_log": "test log line", "source": "firewall"})
    assert r.status_code == 401


def test_stats():
    r = client.get("/stats")
    assert r.status_code == 200
    body = r.json()
    assert "total_events" in body
    assert "by_risk_level" in body
