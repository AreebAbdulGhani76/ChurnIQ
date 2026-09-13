# 🔄 Telco Customer Churn — End-to-End ML Pipeline

A production-grade machine learning pipeline that predicts telecom customer churn, covering the full ML lifecycle: data ingestion → preprocessing → feature engineering → model training with experiment tracking → REST API serving → containerization → CI/CD → monitoring.

---

## 🏗️ Architecture

```
┌──────────────┐    ┌──────────────────┐    ┌───────────────┐
│  Raw CSV     │───▶│  Data Ingestion  │───▶│  Feature Eng  │
│  (7,043 rows)│    │  (validate,fix)  │    │  (derive cols)│
└──────────────┘    └──────────────────┘    └───────┬───────┘
                                                    │
                                                    ▼
                    ┌──────────────────┐    ┌───────────────┐
                    │  MLflow Tracking │◀───│ Preprocessing │
                    │  (params,metrics)│    │ (encode,scale)│
                    └────────┬─────────┘    └───────┬───────┘
                             │                      │
                             ▼                      ▼
                    ┌──────────────────┐    ┌───────────────┐
                    │  Model Registry  │◀───│   Training    │
                    │  (best model)    │    │ (LR, RF, XGB) │
                    └────────┬─────────┘    └───────────────┘
                             │
                             ▼
                    ┌──────────────────┐    ┌───────────────┐
                    │  FastAPI Server  │───▶│  Prometheus   │
                    │  /predict        │    │  /metrics     │
                    └──────────────────┘    └───────────────┘
```

## ⚡ Quick Start

### 1. Setup Environment

```bash
# Clone and enter project
cd Telcom_Churn

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Train Models

```bash
python -m src.train
```

This will:
- Ingest and validate the raw CSV
- Engineer features (tenure groups, streaming flags, etc.)
- Preprocess data (encode, scale, split 70/15/15)
- Train 3 models: Logistic Regression, Random Forest, XGBoost
- Log all experiments to MLflow
- Save the best model to `models/best_model.joblib`

### 3. Explore Experiments

```bash
mlflow server --backend-store-uri sqlite:///mlflow.db --port 5000 --workers 1
# Open http://127.0.0.1:5000
```

### 4. Start the API

```bash
uvicorn api.main:app --reload --port 8000
# Open http://localhost:8000/docs for Swagger UI
```

### 5. Make Predictions

```bash
# Single prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "gender": "Female",
    "SeniorCitizen": 0,
    "Partner": "Yes",
    "Dependents": "No",
    "tenure": 1,
    "PhoneService": "No",
    "MultipleLines": "No phone service",
    "InternetService": "DSL",
    "OnlineSecurity": "No",
    "OnlineBackup": "Yes",
    "DeviceProtection": "No",
    "TechSupport": "No",
    "StreamingTV": "No",
    "StreamingMovies": "No",
    "Contract": "Month-to-month",
    "PaperlessBilling": "Yes",
    "PaymentMethod": "Electronic check",
    "MonthlyCharges": 29.85,
    "TotalCharges": 29.85
  }'
```

Response:
```json
{
  "prediction": 1,
  "probability": 0.72,
  "label": "Churn"
}
```

---

## 🧪 Run Tests

```bash
pytest tests/ -v
```

---

## 🐳 Docker

```bash
# Build and run
docker-compose up --build

# API: http://localhost:8000
# MLflow: http://localhost:5000
```

---

## 📁 Project Structure

```
Telcom_Churn/
├── data/
│   ├── raw/                    # Original dataset
│   └── processed/              # Clean Parquet (generated)
├── src/
│   ├── data_ingestion.py       # Load, validate, type-fix
│   ├── feature_engineering.py  # Derived features
│   ├── preprocessing.py        # Encode, scale, split
│   ├── train.py                # Multi-model training + MLflow
│   └── predict.py              # Inference wrapper
├── api/
│   ├── main.py                 # FastAPI application
│   └── schemas.py              # Pydantic models
├── tests/                      # pytest test suite
├── models/                     # Serialized model artifacts
├── monitoring/
│   └── monitoring_plan.md      # Monitoring & alerting strategy
├── mlruns/                     # MLflow tracking (gitignored)
├── .github/workflows/ci.yml    # GitHub Actions CI
├── Dockerfile                  # Multi-stage container build
├── docker-compose.yml          # API + MLflow services
├── requirements.txt            # Python dependencies
├── pyproject.toml              # Project config + ruff
└── README.md
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| ML Framework | scikit-learn, XGBoost |
| Experiment Tracking | MLflow |
| API Framework | FastAPI + Uvicorn |
| Data Processing | pandas, NumPy |
| Testing | pytest, httpx |
| Linting | Ruff |
| Containerization | Docker, Docker Compose |
| CI/CD | GitHub Actions |
| Monitoring | Prometheus + Grafana (planned) |

---

## 📊 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Readiness probe |
| `POST` | `/predict` | Single prediction |
| `POST` | `/predict/batch` | Batch predictions (≤1000) |
| `GET` | `/model/info` | Current model metadata |
| `GET` | `/metrics` | Prometheus metrics |
| `GET` | `/docs` | Swagger UI |

---

## 📝 License

MIT
