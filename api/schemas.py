"""
Pydantic Schemas
================
Request/response models for the FastAPI prediction service.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class CustomerInput(BaseModel):
    """Input features for a single customer prediction."""

    customerID: Optional[str] = Field(None, description="Customer identifier")
    gender: str = Field(..., examples=["Male"], description="Male or Female")
    SeniorCitizen: int = Field(..., ge=0, le=1, examples=[0], description="1 if senior citizen")
    Partner: str = Field(..., examples=["Yes"], description="Has partner (Yes/No)")
    Dependents: str = Field(..., examples=["No"], description="Has dependents (Yes/No)")
    tenure: int = Field(..., ge=0, examples=[12], description="Months with company")
    PhoneService: str = Field(..., examples=["Yes"], description="Has phone service (Yes/No)")
    MultipleLines: str = Field(
        ..., examples=["No"], description="Has multiple lines (Yes/No/No phone service)"
    )
    InternetService: str = Field(
        ..., examples=["DSL"], description="Internet type (DSL/Fiber optic/No)"
    )
    OnlineSecurity: str = Field(
        ..., examples=["No"], description="Online security (Yes/No/No internet service)"
    )
    OnlineBackup: str = Field(
        ..., examples=["Yes"], description="Online backup (Yes/No/No internet service)"
    )
    DeviceProtection: str = Field(
        ..., examples=["No"], description="Device protection (Yes/No/No internet service)"
    )
    TechSupport: str = Field(
        ..., examples=["No"], description="Tech support (Yes/No/No internet service)"
    )
    StreamingTV: str = Field(
        ..., examples=["No"], description="Streaming TV (Yes/No/No internet service)"
    )
    StreamingMovies: str = Field(
        ..., examples=["No"], description="Streaming movies (Yes/No/No internet service)"
    )
    Contract: str = Field(
        ..., examples=["Month-to-month"],
        description="Contract type (Month-to-month/One year/Two year)",
    )
    PaperlessBilling: str = Field(
        ..., examples=["Yes"], description="Paperless billing (Yes/No)"
    )
    PaymentMethod: str = Field(
        ..., examples=["Electronic check"],
        description="Payment method",
    )
    MonthlyCharges: float = Field(..., ge=0, examples=[29.85], description="Monthly charge ($)")
    TotalCharges: float = Field(..., ge=0, examples=[29.85], description="Total charges ($)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
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
                    "TotalCharges": 29.85,
                }
            ]
        }
    }


class PredictionResponse(BaseModel):
    """Response for a single prediction."""

    prediction: int = Field(..., description="0 = No Churn, 1 = Churn")
    probability: float = Field(..., description="Churn probability (0-1)")
    label: str = Field(..., description="Human-readable label")


class BatchPredictionResponse(BaseModel):
    """Response for batch predictions."""

    predictions: List[PredictionResponse]
    count: int


class ModelInfo(BaseModel):
    """Current model metadata."""

    model_name: str
    test_metrics: dict
    feature_count: int


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    model_loaded: bool
