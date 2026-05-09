from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.infrastructure.database import get_db
from app.services.ml_service import MLService
from app.core.exceptions import NoDataError, NoModelError, TrainingError

router = APIRouter()


class TrainRequest(BaseModel):
    algorithm: str = "random_forest"
    target_variable: str = "score"
    test_size: float = 0.2


class PredictionResponse(BaseModel):
    zone_code: str
    zone_name: str
    predicted_value: float
    prediction_label: str
    model_version: str


class TrainResponse(BaseModel):
    status: str
    experiment_id: int
    algorithm: str
    metrics: dict
    model_version: str


def get_ml_service(db: AsyncSession = Depends(get_db)) -> MLService:
    return MLService(db)


@router.post("/train", response_model=TrainResponse)
async def train_model(
        request: TrainRequest = TrainRequest(),
        service: MLService = Depends(get_ml_service)
):
    """Entrena un modelo de ML."""
    try:
        result = await service.train_model(request.dict())
        return result
    except NoDataError as e:
        raise e
    except TrainingError as e:
        raise e
    except Exception as e:
        raise HTTPException(500, detail=f"Error interno: {str(e)}")


@router.get("/predict/{zone_code}", response_model=PredictionResponse)
async def predict_zone(
        zone_code: str,
        service: MLService = Depends(get_ml_service)
):
    """Predice el potencial de una zona."""
    try:
        result = await service.predict_zone(zone_code)
        return result
    except NoModelError as e:
        raise e
    except NoDataError as e:
        raise e
    except Exception as e:
        raise HTTPException(500, detail=f"Error interno: {str(e)}")


@router.get("/experiments")
async def get_experiments(
        service: MLService = Depends(get_ml_service)
):
    """Obtiene todos los experimentos."""
    try:
        return await service.get_experiments()
    except Exception as e:
        raise HTTPException(500, detail=f"Error interno: {str(e)}")


@router.get("/predictions")
async def get_predictions(
        zone_code: Optional[str] = None,
        service: MLService = Depends(get_ml_service)
):
    """Obtiene predicciones realizadas."""
    try:
        return await service.get_predictions(zone_code)
    except Exception as e:
        raise HTTPException(500, detail=f"Error interno: {str(e)}")