import pickle
import os
import uuid
import numpy as np
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.interfaces import IModelTrainer, IMLRepository
from app.services.model_trainer import RandomForestTrainer
from app.services.analytics_client import AnalyticsClient
from app.repositories.ml_repository import MLRepository
from app.core.exceptions import NoDataError, NoModelError, TrainingError
from app.domain.models import PredictionResult
from sqlalchemy import select


class MLService:
    """Servicio de Machine Learning"""

    def __init__(
            self,
            db: AsyncSession,
            trainer: Optional[IModelTrainer] = None,
            repository: Optional[IMLRepository] = None,
            analytics_client: Optional[AnalyticsClient] = None
    ):
        self.db = db
        self.trainer = trainer or RandomForestTrainer()
        self.repository = repository or MLRepository(db)
        self.analytics_client = analytics_client or AnalyticsClient()
        self._model_path = "/app/models"
        os.makedirs(self._model_path, exist_ok=True)
        self._current_model = self._load_model_from_disk()

    def _save_model_to_disk(self, model, model_id: int) -> str:
        """Guarda el modelo en disco."""
        path = f"{self._model_path}/model_{model_id}.pkl"
        with open(path, 'wb') as f:
            pickle.dump(model, f)
        return path

    def _load_model_from_disk(self):
        """Carga el modelo más reciente desde disco."""
        if not os.path.exists(self._model_path):
            return None

        files = [f for f in os.listdir(self._model_path) if f.endswith('.pkl')]
        if not files:
            return None

        latest_file = sorted(files)[-1]
        path = f"{self._model_path}/{latest_file}"
        with open(path, 'rb') as f:
            return pickle.load(f)

    async def train_model(self, config: Dict = None) -> Dict:
        """Entrena un modelo de ML."""
        config = config or {}
        algorithm = config.get("algorithm", "random_forest")
        target_variable = config.get("target_variable", "score")
        test_size = config.get("test_size", 0.2)

        # Obtener datos de entrenamiento
        try:
            training_data = await self.analytics_client.get_training_data()
        except Exception as e:
            raise NoDataError()

        if not training_data or not training_data.get("features"):
            raise NoDataError()

        features = training_data["features"]
        target = training_data["target"]
        feature_names = training_data.get("feature_names", [])

        # Seleccionar entrenador según algoritmo
        if algorithm == "linear_regression":
            from app.services.model_trainer import LinearRegressionTrainer
            self.trainer = LinearRegressionTrainer()
        else:
            self.trainer = RandomForestTrainer()

        # Entrenar modelo
        try:
            model = self.trainer.train(features, target)
            self._current_model = model
        except Exception as e:
            raise TrainingError(str(e))

        # Evaluar modelo
        metrics = self.trainer.evaluate(model, features, target)

        # Guardar experimento
        experiment_id = await self.repository.save_experiment({
            "name": f"Experiment_{uuid.uuid4().hex[:8]}",
            "target_variable": target_variable,
            "algorithm": algorithm,
            "features_used": feature_names,
            "evaluation_metric": "r2",
            "metric_value": metrics.get("r2", 0)
        })

        # Guardar modelo en disco
        self._save_model_to_disk(model, experiment_id)

        # Guardar metadatos del modelo
        model_version = f"v{experiment_id}.0"
        await self.repository.save_model({
            "experiment_id": experiment_id,
            "model_name": f"TerritorialPredictor_{algorithm}",
            "model_version": model_version,
            "storage_path": f"/app/models/model_{experiment_id}.pkl"
        })

        return {
            "status": "completed",
            "experiment_id": experiment_id,
            "algorithm": algorithm,
            "metrics": metrics,
            "model_version": model_version
        }

    async def predict_zone(self, zone_code: str) -> Dict:
        """Predice el potencial de una zona."""
        # Verificar que hay un modelo entrenado
        model_info = await self.repository.get_active_model()
        if not model_info and self._current_model is None:
            raise NoModelError()

        # Intentar cargar desde disco si no está en memoria
        if self._current_model is None:
            self._current_model = self._load_model_from_disk()
            if self._current_model is None:
                raise NoModelError()

        # Obtener datos de la zona
        try:
            zone_data = await self.analytics_client.get_zone_data(zone_code)
        except Exception as e:
            raise NoDataError()

        # Extraer features
        features = [[
            zone_data.get("contributions", {}).get("population", 0),
            zone_data.get("contributions", {}).get("income", 0),
            zone_data.get("contributions", {}).get("education", 0),
            zone_data.get("contributions", {}).get("competition_penalty", 0)
        ]]

        # Predecir
        prediction = self.trainer.predict(self._current_model, features)[0]

        # Guardar predicción
        if model_info:
            await self.repository.save_prediction({
                "model_id": model_info["id"],
                "zone_code": zone_code,
                "zone_name": zone_data.get("zone_name", ""),
                "prediction_value": round(prediction, 2),
                "prediction_label": await self._get_opportunity_label(prediction),
                "confidence_score": None
            })

        return {
            "zone_code": zone_code,
            "zone_name": zone_data.get("zone_name", ""),
            "predicted_value": round(prediction, 2),
            "prediction_label": await self._get_opportunity_label(prediction),
            "model_version": model_info["model_version"] if model_info else "unknown"
        }

    async def _get_opportunity_label(self, value: float) -> str:
        """
        Clasifica el nivel de oportunidad usando percentiles.

        Si no hay datos suficientes, devuelve "Sin clasificar"
        """
    # obtener valores históricos para calcular percentiles
        all_values = self._get_all_prediction_values()

        if all_values and len(all_values) >= 3:

            p75 = np.percentile(all_values, 75)
            p25 = np.percentile(all_values, 25)

            if value >= p75:
                return "Alta"
            elif value >= p25:
                return "Media"
            return "Baja"

        return "Sin clasificar"

    async def get_experiments(self) -> list:
        return await self.repository.get_experiments()

    async def get_predictions(self, zone_code: str = None) -> list:
        return await self.repository.get_predictions(zone_code)

    def _get_all_prediction_values(self) -> List[float]:
        """valores de predicciones guardadas en BD."""
        try:
            return []
        except Exception:
            return []
