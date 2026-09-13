"""
FastAPI Application
===================
REST API for Telco Customer Churn predictions.

Endpoints:
  GET  /health         — readiness / liveness probe
  POST /predict        — single-customer prediction
  POST /predict/batch  — batch predictions
  GET  /model/info     — currently loaded model metadata
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator

from api.schemas import (
    BatchPredictionResponse,
    CustomerInput,
    HealthResponse,
    ModelInfo,
    PredictionResponse,
)
from src.predict import ChurnPredictor

logger = logging.getLogger(__name__)

# ── Global predictor (loaded once at startup) ────────────────────────────────
predictor: ChurnPredictor = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model on startup, cleanup on shutdown."""
    global predictor
    try:
        predictor = ChurnPredictor()
        logger.info("Model loaded successfully")
    except FileNotFoundError:
        logger.warning(
            "Model files not found. Run 'python -m src.train' first. "
            "API will start but predictions will fail."
        )
    yield
    logger.info("Shutting down…")


# ── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Telco Churn Prediction API",
    description=(
        "End-to-end ML pipeline API for predicting customer churn. "
        "Trained on the Telco Customer Churn dataset using scikit-learn / XGBoost "
        "with MLflow experiment tracking."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics
Instrumentator().instrument(app).expose(app)

# ── Static Assets & Web App UI ───────────────────────────────────────────────
STATIC_DIR = Path(__file__).resolve().parent / "static"
ARTIFACTS_DIR = Path(__file__).resolve().parent.parent / "models" / "artifacts"

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

if ARTIFACTS_DIR.exists():
    app.mount("/artifacts", StaticFiles(directory=str(ARTIFACTS_DIR)), name="artifacts")


# ── Routes ───────────────────────────────────────────────────────────────────
@app.get("/", response_class=FileResponse, tags=["Web App"])
async def serve_ui():
    """Serve the Web Application."""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "Telco Churn Prediction API is running. Visit /docs for API documentation."}


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Readiness / liveness probe."""
    return HealthResponse(
        status="healthy",
        model_loaded=predictor is not None,
    )


@app.post("/predict", response_model=PredictionResponse, tags=["Predictions"])
async def predict_single(customer: CustomerInput):
    """Predict churn for a single customer."""
    if predictor is None:
        raise HTTPException(status_code=503, detail="Model not loaded. Train a model first.")

    try:
        data = customer.model_dump(exclude={"customerID"})
        result = predictor.predict(data)
        return PredictionResponse(**result)
    except Exception as e:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@app.post("/predict/batch", response_model=BatchPredictionResponse, tags=["Predictions"])
async def predict_batch(customers: List[CustomerInput]):
    """Predict churn for a batch of customers."""
    if predictor is None:
        raise HTTPException(status_code=503, detail="Model not loaded. Train a model first.")

    if len(customers) > 1000:
        raise HTTPException(status_code=400, detail="Batch size limited to 1000 customers.")

    try:
        import pandas as pd

        records = [c.model_dump(exclude={"customerID"}) for c in customers]
        df = pd.DataFrame(records)
        results = predictor.predict(df)

        # Single result → wrap in list
        if isinstance(results, dict):
            results = [results]

        return BatchPredictionResponse(
            predictions=[PredictionResponse(**r) for r in results],
            count=len(results),
        )
    except Exception as e:
        logger.exception("Batch prediction failed")
        raise HTTPException(status_code=500, detail=f"Batch prediction error: {str(e)}")


@app.get("/model/info", response_model=ModelInfo, tags=["Model"])
async def model_info():
    """Return metadata about the currently loaded model."""
    if predictor is None:
        raise HTTPException(status_code=503, detail="Model not loaded.")

    info = predictor.get_model_info()
    return ModelInfo(**info)
