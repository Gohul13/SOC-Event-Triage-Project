"""POST sample logs from the training CSV into the running API (optional demo helper)."""

from __future__ import annotations

import csv
import os
import re
import sys
from pathlib import Path

import httpx

REPO = Path(__file__).resolve().parents[2]
CSV_PATH = REPO / "ml" / "data" / "sample_logs.csv"

SOURCE_PATTERNS = [
    (re.compile(r"\bfirewall\b", re.I), "firewall"),
    (re.compile(r"\bauth\b", re.I), "auth"),
    (re.compile(r"\bids\b", re.I), "ids"),
    (re.compile(r"\bendpoint\b", re.I), "endpoint"),
    (re.compile(r"\bproxy\b", re.I), "proxy"),
    (re.compile(r"\bwaf\b", re.I), "waf"),
    (re.compile(r"\bantivirus\b", re.I), "antivirus"),
    (re.compile(r"\bdns\b", re.I), "dns"),
]


def infer_source(log_line: str) -> str:
    for pattern, name in SOURCE_PATTERNS:
        if pattern.search(log_line):
            return name
    return "unknown"


def main() -> None:
    base = os.environ.get("API_BASE", "http://127.0.0.1:8000")
    api_key = os.environ.get("API_KEY", "dev-api-key-change-in-production")
    limit = int(os.environ.get("SEED_LIMIT", "15"))

    rows: list[dict[str, str]] = []
    with CSV_PATH.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= limit:
                break
            log = row["log_line"]
            rows.append({"raw_log": log, "source": infer_source(log)})

    with httpx.Client(base_url=base, headers={"X-API-Key": api_key}, timeout=30.0) as client:
        r = client.post("/events", json={"events": rows})
        if r.status_code >= 400:
            print(r.status_code, r.text, file=sys.stderr)
            sys.exit(1)
        print(f"Seeded {len(r.json())} events")


if __name__ == "__main__":
    main()
