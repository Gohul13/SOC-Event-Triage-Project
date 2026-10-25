# Raksha SOC — Security Event Triage Dashboard

Mini full-stack application for ingesting security log lines, classifying risk with a lightweight ML model (Benign / Suspicious / Malicious), and triaging events from a React analyst dashboard.

## Architecture

```text
┌─────────────┐     REST (JSON)      ┌──────────────────┐
│ React UI    │ ◄──────────────────► │ FastAPI backend  │
│ (Vite)      │   GET /events/stats  │  + SQLite        │
└─────────────┘   POST/PATCH + API key └────────┬─────────┘
                                                 │
                                                 ▼
                                        TF-IDF + Logistic Regression
                                        (joblib artifact from ml/train.py)
```

| Layer | Path | Role |
|--------|------|------|
| Frontend | `frontend/` | Dashboard, filters, chart, detail panel, status updates |
| Backend | `backend/app/` | REST API, validation, auth, persistence |
| ML | `ml/` | Labeled sample data, training script, model artifact |

## Assumptions

- **Auth**: Write endpoints (`POST /events`, `PATCH /events/{id}`) require header `X-API-Key`. Read endpoints are open for the local demo dashboard (documented in README; tighten in production).
- **Classification**: Runs synchronously on ingest; confidence is the predicted class probability from logistic regression.
- **Status**: New events start as `Pending`; analysts set `Reviewed`, `False Positive`, or `Escalated` via PATCH/UI.
- **Dataset**: Synthetic log lines in `ml/data/sample_logs.csv` (60 rows), inspired by common SOC log patterns—not real customer data.

## Prerequisites

- Python 3.11+
- Node.js 18+

## Setup

### 1. Python environment & model

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
python ml/train.py
```

Training writes:

- `ml/models/log_classifier.joblib`
- `ml/models/training_metrics.json` (accuracy, macro F1, classification report)

**Validation approach**: stratified 75/25 train/test split (`random_state=42`), reporting accuracy and macro F1 on the holdout set.

### 2. Backend

```powershell
cd backend
copy .env.example .env
# Edit API_KEY if desired
mkdir data -Force
uvicorn app.main:app --reload --port 8000
```

API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 3. Frontend

```powershell
cd frontend
copy .env.example .env
# Set VITE_API_KEY to match backend API_KEY
npm install
npm run dev
```

Open [http://127.0.0.1:5173](http://127.0.0.1:5173). Vite proxies `/api` → backend.

### 4. Seed demo events (optional)

With the API running:

```powershell
$env:API_KEY = "dev-api-key-change-in-production"  # match .env
python backend/scripts/seed_sample_events.py
```

## API summary

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/events` | Yes | Single event, `{ "events": [...] }`, or JSON array |
| GET | `/events` | No | Filter: `risk_level`, `source`, `status`, `from`, `to` |
| GET | `/events/{id}` | No | Event detail |
| PATCH | `/events/{id}` | Yes | Body: `{ "status": "Reviewed" \| "False Positive" \| "Escalated" }` |
| GET | `/stats` | No | Totals by risk and source |

## Retrain the model

After editing `ml/data/sample_logs.csv`:

```powershell
python ml/train.py
```

Restart the backend to reload the classifier (or redeploy).

## Tests

```powershell
cd backend
pytest tests/ -q
```

## Project structure

```text
raksha-soc-triage/
├── backend/
│   ├── app/           # FastAPI application
│   ├── scripts/       # Seed helper
│   └── tests/
├── frontend/          # React dashboard
├── ml/
│   ├── data/          # Labeled training CSV
│   ├── models/        # Generated artifacts
│   └── train.py
└── README.md
```

## External data

All training labels are **synthetic** lines authored for this assignment. No third-party log dump was copied verbatim.
