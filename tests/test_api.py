"""
Tests for the FastAPI application.
Uses TestClient to test endpoints without running a server.
"""

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

# We need to patch the predictor before importing the app
from api.main import app


@pytest.fixture
def client():
    """TestClient fixture."""
    return TestClient(app)


@pytest.fixture
def sample_customer():
    """Minimal valid customer payload."""
    return {
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


class TestRootUIEndpoint:
    def test_root_returns_html_or_json(self, client):
        response = client.get("/")
        assert response.status_code == 200
        # Should either serve HTML or fallback json
        assert "text/html" in response.headers.get("content-type", "") or "application/json" in response.headers.get("content-type", "")


class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "model_loaded" in data


class TestPredictEndpoint:
    def test_predict_returns_503_without_model(self, client, sample_customer):
        """If model is not loaded, should return 503."""
        import api.main as api_module
        original = api_module.predictor
        api_module.predictor = None
        try:
            response = client.post("/predict", json=sample_customer)
            assert response.status_code == 503
        finally:
            api_module.predictor = original

    def test_predict_with_mock_model(self, client, sample_customer):
        """Mock the predictor to test the endpoint logic."""
        import api.main as api_module

        mock_predictor = MagicMock()
        mock_predictor.predict.return_value = {
            "prediction": 1,
            "probability": 0.85,
            "label": "Churn",
        }

        original = api_module.predictor
        api_module.predictor = mock_predictor
        try:
            response = client.post("/predict", json=sample_customer)
            assert response.status_code == 200
            data = response.json()
            assert data["prediction"] == 1
            assert data["probability"] == 0.85
            assert data["label"] == "Churn"
        finally:
            api_module.predictor = original

    def test_predict_validates_input(self, client):
        """Missing required fields should return 422."""
        response = client.post("/predict", json={"gender": "Male"})
        assert response.status_code == 422


class TestBatchEndpoint:
    def test_batch_with_mock(self, client, sample_customer):
        import api.main as api_module

        mock_predictor = MagicMock()
        mock_predictor.predict.return_value = [
            {"prediction": 0, "probability": 0.2, "label": "No Churn"},
            {"prediction": 1, "probability": 0.9, "label": "Churn"},
        ]

        original = api_module.predictor
        api_module.predictor = mock_predictor
        try:
            response = client.post("/predict/batch", json=[sample_customer, sample_customer])
            assert response.status_code == 200
            data = response.json()
            assert data["count"] == 2
            assert len(data["predictions"]) == 2
        finally:
            api_module.predictor = original


class TestModelInfoEndpoint:
    def test_model_info_returns_503_without_model(self, client):
        import api.main as api_module
        original = api_module.predictor
        api_module.predictor = None
        try:
            response = client.get("/model/info")
            assert response.status_code == 503
        finally:
            api_module.predictor = original

    def test_model_info_with_mock(self, client):
        import api.main as api_module

        mock_predictor = MagicMock()
        mock_predictor.get_model_info.return_value = {
            "model_name": "XGBoost",
            "test_metrics": {"accuracy": 0.80, "f1": 0.65},
            "feature_count": 30,
        }

        original = api_module.predictor
        api_module.predictor = mock_predictor
        try:
            response = client.get("/model/info")
            assert response.status_code == 200
            data = response.json()
            assert data["model_name"] == "XGBoost"
        finally:
            api_module.predictor = original
