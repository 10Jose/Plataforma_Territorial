import pickle
import os
from typing import Any, Dict
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
import numpy as np
from app.domain.interfaces import IModelTrainer


class RandomForestTrainer(IModelTrainer):
    """Entrenador con Random Forest."""

    def __init__(self, n_estimators: int = 100, random_state: int = 42):
        self.model = RandomForestRegressor(
            n_estimators=n_estimators,
            random_state=random_state
        )
        self._trained_model = None

    def get_algorithm_name(self) -> str:
        return "random_forest"

    def train(self, features: list, target: list) -> Any:
        self._trained_model = self.model.fit(features, target)
        return self._trained_model

    def predict(self, model: Any, features: list) -> list:
        return model.predict(features).tolist()

    def evaluate(self, model: Any, features: list, target: list) -> Dict[str, float]:
        predictions = model.predict(features)
        return {
            "mse": float(mean_squared_error(target, predictions)),
            "rmse": float(np.sqrt(mean_squared_error(target, predictions))),
            "r2": float(r2_score(target, predictions))
        }


class LinearRegressionTrainer(IModelTrainer):
    """Entrenador con Regresión Lineal."""

    def __init__(self):
        self.model = LinearRegression()
        self._trained_model = None

    def get_algorithm_name(self) -> str:
        return "linear_regression"

    def train(self, features: list, target: list) -> Any:
        self._trained_model = self.model.fit(features, target)
        return self._trained_model

    def predict(self, model: Any, features: list) -> list:
        return model.predict(features).tolist()

    def evaluate(self, model: Any, features: list, target: list) -> Dict[str, float]:
        predictions = model.predict(features)
        return {
            "mse": float(mean_squared_error(target, predictions)),
            "rmse": float(np.sqrt(mean_squared_error(target, predictions))),
            "r2": float(r2_score(target, predictions))
        }