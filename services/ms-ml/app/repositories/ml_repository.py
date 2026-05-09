from typing import List, Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.domain.models import MLExperiment, TrainedModel, PredictionResult
from app.domain.interfaces import IMLRepository


class MLRepository(IMLRepository):
    """Repositorio para ML."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_experiment(self, experiment_data: Dict) -> int:
        experiment = MLExperiment(
            name=experiment_data["name"],
            problem_type=experiment_data.get("problem_type", "regression"),
            target_variable=experiment_data["target_variable"],
            algorithm=experiment_data["algorithm"],
            features_used=experiment_data.get("features_used"),
            evaluation_metric=experiment_data.get("evaluation_metric"),
            metric_value=experiment_data.get("metric_value"),
            status="completed"
        )
        self.db.add(experiment)
        await self.db.commit()
        await self.db.refresh(experiment)
        return experiment.id

    async def save_model(self, model_data: Dict) -> int:
        # Desactivar modelo anterior
        await self.db.execute(
            update(TrainedModel).values(is_active=False)
        )

        model = TrainedModel(
            experiment_id=model_data["experiment_id"],
            model_name=model_data["model_name"],
            model_version=model_data["model_version"],
            storage_path=model_data.get("storage_path"),
            status="active",
            is_active=True
        )
        self.db.add(model)
        await self.db.commit()
        await self.db.refresh(model)
        return model.id

    async def save_prediction(self, prediction_data: Dict) -> None:
        prediction = PredictionResult(
            model_id=prediction_data["model_id"],
            zone_code=prediction_data["zone_code"],
            zone_name=prediction_data["zone_name"],
            prediction_value=prediction_data["prediction_value"],
            prediction_label=prediction_data.get("prediction_label"),
            confidence_score=prediction_data.get("confidence_score")
        )
        self.db.add(prediction)
        await self.db.commit()

    async def get_active_model(self) -> Optional[Dict]:
        stmt = select(TrainedModel).where(TrainedModel.is_active == True)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return {
            "id": model.id,
            "experiment_id": model.experiment_id,
            "model_name": model.model_name,
            "model_version": model.model_version,
            "storage_path": model.storage_path,
            "trained_at": model.trained_at
        }

    async def get_experiments(self) -> list:
        stmt = select(MLExperiment).order_by(MLExperiment.executed_at.desc())
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_predictions(self, zone_code: Optional[str] = None) -> list:
        stmt = select(PredictionResult).order_by(PredictionResult.predicted_at.desc())
        if zone_code:
            stmt = stmt.where(PredictionResult.zone_code == zone_code)
        result = await self.db.execute(stmt)
        return result.scalars().all()