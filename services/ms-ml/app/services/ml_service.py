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
from sqlalchemy import delete
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
        all_values = await self._get_all_prediction_values()

        if all_values and len(all_values) >= 3:

            p75 = np.percentile(all_values, 75)
            p25 = np.percentile(all_values, 25)

            if value >= p75:
                return "Alta"
            elif value >= p25:
                return "Media"
            return "Baja"

        return "Sin clasificar"


    async def _get_all_prediction_values(self) -> List[float]:
        """Obtiene valores para calcular percentiles usando SOLO scores reales."""
        all_values = []
        try:
            scores = await self.analytics_client.get_all_scores()
            if scores:
                return [s.get("score", 0) for s in scores]
        except Exception:
            pass

        try:
            predictions = await self.repository.get_predictions()
            if predictions:
                all_values.extend([p.prediction_value for p in predictions])
        except Exception:
            pass

        return all_values


    async def get_experiments(self) -> list:
        return await self.repository.get_experiments()

    async def get_predictions(self, zone_code: str = None) -> list:
        return await self.repository.get_predictions(zone_code)

    async def predict_all_zones(self) -> Dict:
        """Predice el potencial de todas las zonas disponibles"""
        model_info = await self.repository.get_active_model()
        if not model_info and self._current_model is None:
            raise NoModelError()

        if self._current_model is None:
            self._current_model = self._load_model_from_disk()
            if self._current_model is None:
                raise NoModelError()

        try:
            scores = await self.analytics_client.get_all_scores()
        except Exception as e:
            raise NoDataError()

        if not scores:
            raise NoDataError()

        results = []
        new_predictions = 0
        skipped_predictions = 0
        updated_predictions = 0

        for zone in scores:
            zone_code = zone.get("zone_code", "")
            zone_name = zone.get("zone_name", "")
            contributions = zone.get("contributions", {})
            current_score = zone.get("score", 0)

        # Verificar predicción para esta zona
            existing_predictions = await self.repository.get_predictions(zone_code)

            if existing_predictions:
                latest = existing_predictions[0]

            # Verificar score real cambió significativamente
                score_changed = abs(latest.prediction_value - current_score) > 1.0 if current_score else False

                if not score_changed:
                # usar predicción existente
                    results.append({
                        "zone_code": zone_code,
                        "zone_name": zone_name,
                        "predicted_value": latest.prediction_value,
                        "prediction_label": latest.prediction_label,
                        "actual_score": current_score,
                        "status": "unchanged"
                    })
                    skipped_predictions += 1
                    continue

            features = [[
                contributions.get("population", 0),
                contributions.get("income", 0),
                contributions.get("education", 0),
                contributions.get("competition_penalty", 0)
            ]]

            prediction = self.trainer.predict(self._current_model, features)[0]
            label = await self._get_opportunity_label(prediction)

            await self.repository.save_prediction({
                "model_id": model_info["id"] if model_info else 1,
                "zone_code": zone_code,
                "zone_name": zone_name,
                "prediction_value": round(prediction, 2),
                "prediction_label": label,
                "confidence_score": None
            })

            status = "updated" if existing_predictions else "new"
            if existing_predictions:
                updated_predictions += 1
            else:
                new_predictions += 1

            results.append({
                "zone_code": zone_code,
                "zone_name": zone_name,
                "predicted_value": round(prediction, 2),
                "prediction_label": label,
                "actual_score": current_score,
                "status": status
            })

        return {
            "status": "completed",
            "zones_processed": len(results),
            "new_predictions": new_predictions,
            "updated_predictions": updated_predictions,
            "skipped_predictions": skipped_predictions,
            "predictions": results,
            "model_version": model_info["model_version"] if model_info else "unknown"
        }

    async def get_prediction_stats(self) -> Dict:
        """Obtiene estadísticas comparativas de predicciones."""
        predictions = await self.repository.get_predictions()

        if not predictions:
            return {"status": "no_data", "message": "No hay predicciones aún"}

        values = [p.prediction_value for p in predictions]

        return {
            "total_predictions": len(predictions),
            "average_prediction": round(np.mean(values), 2),
            "max_prediction": round(max(values), 2),
            "min_prediction": round(min(values), 2),
            "standard_deviation": round(np.std(values), 2),
            "by_level": {
                "Alta": len([v for v in values if v >= np.percentile(values, 75)]),
                "Media": len([v for v in values if np.percentile(values, 25) <= v < np.percentile(values, 75)]),
                "Baja": len([v for v in values if v < np.percentile(values, 25)])
            },
            "thresholds": {
                "P75": round(np.percentile(values, 75), 2),
                "P25": round(np.percentile(values, 25), 2)
            }
    }

    async def clear_predictions(self) -> None:
        """Limpia todas las predicciones guardadas."""
        await self.db.execute(delete(PredictionResult))
        await self.db.commit()

    async def compare_prediction(self, zone_code: str) -> Dict:
        """Compara predicción vs score real para una zona."""
        predictions = await self.repository.get_predictions(zone_code)
        if not predictions:
            return {"status": "no_data", "message": "No hay predicción para esta zona"}

        latest_pred = predictions[0]

    # Obtener score real
        try:
            real_score = await self.analytics_client.get_zone_data(zone_code)
            actual_score = real_score.get("score", None)
        except Exception:
            actual_score = None

        result = {
            "zone_code": zone_code,
            "zone_name": latest_pred.zone_name,
            "predicted_value": latest_pred.prediction_value,
            "prediction_label": latest_pred.prediction_label
        }

        if actual_score is not None:
            difference = round(latest_pred.prediction_value - actual_score, 2)
            result["actual_score"] = actual_score
            result["difference"] = difference
            result["accuracy"] = "Alta" if abs(difference) < 10 else "Media" if abs(difference) < 20 else "Baja"

        return result