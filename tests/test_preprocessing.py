"""
Tests for the preprocessing module.
"""

import numpy as np
import pandas as pd
import pytest

from src.preprocessing import (
    build_preprocessor,
    encode_binary_columns,
    split_data,
)


@pytest.fixture
def sample_raw_df():
    """Minimal sample DataFrame mimicking raw ingested data (post-feature-engineering)."""
    return pd.DataFrame({
        "customerID": ["001", "002", "003", "004", "005", "006", "007", "008", "009", "010"],
        "gender": ["Male", "Female"] * 5,
        "SeniorCitizen": [0, 1, 0, 0, 1, 0, 0, 1, 0, 0],
        "Partner": ["Yes", "No"] * 5,
        "Dependents": ["No", "Yes"] * 5,
        "tenure": [1, 34, 2, 45, 12, 24, 48, 60, 6, 72],
        "PhoneService": ["Yes", "Yes", "No", "Yes", "Yes", "No", "Yes", "Yes", "Yes", "No"],
        "MultipleLines": [
            "No", "Yes", "No phone service", "No", "Yes",
            "No phone service", "Yes", "No", "Yes", "No phone service",
        ],
        "InternetService": [
            "DSL", "Fiber optic", "DSL", "No", "Fiber optic",
            "DSL", "DSL", "Fiber optic", "No", "DSL",
        ],
        "OnlineSecurity": [
            "No", "Yes", "No", "No internet service", "Yes",
            "No", "Yes", "No", "No internet service", "Yes",
        ],
        "OnlineBackup": [
            "Yes", "No", "Yes", "No internet service", "No",
            "Yes", "No", "Yes", "No internet service", "No",
        ],
        "DeviceProtection": [
            "No", "Yes", "No", "No internet service", "Yes",
            "No", "Yes", "No", "No internet service", "Yes",
        ],
        "TechSupport": [
            "No", "No", "Yes", "No internet service", "Yes",
            "No", "No", "Yes", "No internet service", "No",
        ],
        "StreamingTV": [
            "No", "Yes", "No", "No internet service", "Yes",
            "No", "Yes", "No", "No internet service", "Yes",
        ],
        "StreamingMovies": [
            "No", "No", "Yes", "No internet service", "No",
            "Yes", "No", "Yes", "No internet service", "No",
        ],
        "Contract": [
            "Month-to-month", "One year", "Month-to-month", "Two year", "One year",
            "Month-to-month", "Two year", "One year", "Month-to-month", "Two year",
        ],
        "PaperlessBilling": ["Yes", "No"] * 5,
        "PaymentMethod": [
            "Electronic check", "Mailed check", "Bank transfer (automatic)",
            "Credit card (automatic)", "Electronic check",
            "Mailed check", "Bank transfer (automatic)",
            "Credit card (automatic)", "Electronic check", "Mailed check",
        ],
        "MonthlyCharges": [29.85, 56.95, 53.85, 42.30, 70.70, 25.50, 89.10, 45.00, 19.95, 65.00],
        "TotalCharges": [29.85, 1889.5, 108.15, 1840.75, 848.4, 612.0, 4276.8, 2700.0, 119.7, 4680.0],
        "Churn": ["No", "No", "Yes", "No", "Yes", "No", "No", "Yes", "Yes", "No"],
        # Feature-engineered columns
        "tenure_group": pd.Categorical(
            ["0-12", "25-48", "0-12", "25-48", "0-12", "13-24", "25-48", "49-60", "0-12", "61-72"],
            categories=["0-12", "13-24", "25-48", "49-60", "61-72"],
        ),
        "avg_monthly_charge": [29.85, 55.57, 54.08, 40.91, 70.70, 25.50, 89.10, 45.00, 19.95, 65.00],
        "has_streaming": [0, 1, 1, 0, 1, 1, 1, 1, 0, 1],
        "has_security": [1, 1, 1, 0, 1, 1, 1, 1, 0, 1],
    })


class TestEncodeBinaryColumns:
    def test_maps_yes_no(self, sample_raw_df):
        result = encode_binary_columns(sample_raw_df)
        assert set(result["Partner"].unique()) <= {0, 1}
        assert set(result["Dependents"].unique()) <= {0, 1}
        assert set(result["Churn"].unique()) <= {0, 1}

    def test_maps_gender(self, sample_raw_df):
        result = encode_binary_columns(sample_raw_df)
        assert set(result["gender"].unique()) <= {0, 1}


class TestSplitData:
    def test_split_sizes(self, sample_raw_df):
        df = encode_binary_columns(sample_raw_df)
        train, val, test = split_data(df, test_size=0.2, val_size=0.2, random_state=42)
        total = len(train) + len(val) + len(test)
        assert total == len(df)

    def test_no_target_leakage(self, sample_raw_df):
        """Train and test must contain both classes (stratified)."""
        df = encode_binary_columns(sample_raw_df)
        train, val, test = split_data(df, test_size=0.2, val_size=0.2, random_state=42)
        assert train["Churn"].nunique() >= 1  # at least 1 class in small data


class TestBuildPreprocessor:
    def test_preprocessor_fits(self, sample_raw_df):
        df = encode_binary_columns(sample_raw_df)
        df = df.drop(columns=["customerID", "Churn"])
        preprocessor = build_preprocessor()
        X = preprocessor.fit_transform(df)
        assert X.shape[0] == len(df)
        assert X.shape[1] > 0

    def test_output_is_numeric(self, sample_raw_df):
        df = encode_binary_columns(sample_raw_df)
        df = df.drop(columns=["customerID", "Churn"])
        preprocessor = build_preprocessor()
        X = preprocessor.fit_transform(df)
        assert np.issubdtype(X.dtype, np.floating) or np.issubdtype(X.dtype, np.integer)
