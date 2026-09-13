"""
Tests for the training module.
Smoke test: trains on a small subset and verifies metrics/artifacts are produced.
"""


import numpy as np

from src.train import evaluate, get_models


class TestEvaluate:
    def test_returns_all_metrics(self):
        y_true = np.array([0, 1, 1, 0, 1, 0, 1, 0])
        y_pred = np.array([0, 1, 0, 0, 1, 1, 1, 0])
        y_proba = np.array([0.1, 0.9, 0.4, 0.2, 0.8, 0.6, 0.7, 0.3])

        metrics = evaluate(y_true, y_pred, y_proba)
        expected_keys = {"accuracy", "precision", "recall", "f1", "roc_auc", "pr_auc"}
        assert set(metrics.keys()) == expected_keys

    def test_perfect_predictions(self):
        y_true = np.array([0, 1, 0, 1])
        y_pred = np.array([0, 1, 0, 1])
        y_proba = np.array([0.0, 1.0, 0.0, 1.0])

        metrics = evaluate(y_true, y_pred, y_proba)
        assert metrics["accuracy"] == 1.0
        assert metrics["f1"] == 1.0
        assert metrics["roc_auc"] == 1.0

    def test_metric_ranges(self):
        y_true = np.array([0, 1, 1, 0, 1, 0])
        y_pred = np.array([1, 0, 1, 0, 1, 1])
        y_proba = np.array([0.7, 0.3, 0.8, 0.2, 0.9, 0.6])

        metrics = evaluate(y_true, y_pred, y_proba)
        for key, value in metrics.items():
            assert 0.0 <= value <= 1.0, f"{key} out of range: {value}"


class TestGetModels:
    def test_returns_three_models(self):
        models = get_models()
        assert len(models) == 3
        assert "LogisticRegression" in models
        assert "RandomForest" in models
        assert "XGBoost" in models

    def test_models_have_fit_predict(self):
        models = get_models()
        for name, (model, params) in models.items():
            assert hasattr(model, "fit"), f"{name} missing fit()"
            assert hasattr(model, "predict"), f"{name} missing predict()"
            assert hasattr(model, "predict_proba"), f"{name} missing predict_proba()"
            assert isinstance(params, dict), f"{name} params should be dict"

    def test_models_train_on_small_data(self):
        """Smoke test: each model can fit on tiny synthetic data."""
        rng = np.random.RandomState(42)
        X = rng.randn(50, 10)
        y = rng.randint(0, 2, 50)

        models = get_models()
        for name, (model, _) in models.items():
            model.fit(X, y)
            preds = model.predict(X)
            assert len(preds) == 50, f"{name} prediction count mismatch"
            proba = model.predict_proba(X)
            assert proba.shape == (50, 2), f"{name} proba shape mismatch"
