# Raksha SOC – Security Event Triage Dashboard

A full-stack security event triage application that ingests security logs, classifies them as **Benign, Suspicious, or Malicious** using Machine Learning, and allows analysts to review and manage events through a React dashboard.

## Tech Stack

- **Frontend:** React.js, Vite
- **Backend:** Python, FastAPI
- **Database:** SQLite
- **Machine Learning:** TF-IDF, Logistic Regression
- **API:** REST API with API key authentication for write operations

## Features

- Ingest security log events
- Automatically classify events based on risk
- View and filter events by risk level, source, and status
- View event details and statistics
- Update event status to Reviewed, False Positive, or Escalated
- Train and evaluate the ML model using sample log data

## Project Structure

```text
raksha-soc-triage/
├── backend/
│   ├── app/
│   ├── scripts/
│   └── tests/
├── frontend/
├── ml/
│   ├── data/
│   ├── models/
│   └── train.py
└── README.md 
```


### 1. Set Up the Backend

From the project root, run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
python ml/train.py
```

### 2. Start the Backend

```powershell
cd backend
Copy-Item .env.example .env
uvicorn app.main:app --reload --port 8000
```

API documentation: http://127.0.0.1:8000/docs

### 3. Start the Frontend

Open a new terminal:

```powershell
cd frontend
Copy-Item .env.example .env
npm install
npm run dev
```

Open http://127.0.0.1:5173 in your browser.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/events` | Ingest security events |
| GET | `/events` | Retrieve and filter events |
| GET | `/events/{id}` | View event details |
| PATCH | `/events/{id}` | Update event status |
| GET | `/stats` | Retrieve event statistics |


## Machine Learning

The model uses TF-IDF and Logistic Regression to classify security logs. The training dataset contains synthetic sample logs created for this project.

To retrain the model, run:

```powershell
python ml/train.py
```

## Run Tests

From the project root:

```powershell
cd backend
pytest tests/ -q
```
