from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List, Dict
from pydantic import BaseModel
from app.services.ml_client import MLClient
from app.routers.auth import get_current_user
from app.domain.models import User

router = APIRouter()


class TrainRequest(BaseModel):
    algorithm: str = "random_forest"
    target_variable: str = "score"
    test_size: float = 0.2


class TrainResponse(BaseModel):
    status: str
    experiment_id: int
    algorithm: str
    metrics: dict
    model_version: str


class PredictionResponse(BaseModel):
    zone_code: str
    zone_name: str
    predicted_value: float
    prediction_label: str
    model_version: str


class ExperimentResponse(BaseModel):
    id: int
    name: str
    algorithm: str
    target_variable: str
    evaluation_metric: str
    metric_value: float
    status: str
    executed_at: str


@router.post("/train", response_model=TrainResponse)
async def train_model(
        request: TrainRequest = TrainRequest(),
        current_user: User = Depends(get_current_user)
):
    """Entrena un modelo de ML."""
    try:
        client = MLClient()
        result = await client.train_model(request.dict())
        return result
    except Exception as e:
        raise HTTPException(500, detail=f"Error al entrenar modelo: {str(e)}")


@router.get("/predict/{zone_code}", response_model=PredictionResponse)
async def predict_zone(
        zone_code: str,
        current_user: User = Depends(get_current_user)
):
    """Predice el potencial de una zona."""
    try:
        client = MLClient()
        result = await client.predict_zone(zone_code)
        return result
    except Exception as e:
        raise HTTPException(500, detail=f"Error al predecir: {str(e)}")


@router.get("/experiments", response_model=List[ExperimentResponse])
async def get_experiments(
        current_user: User = Depends(get_current_user)
):
    """Obtiene todos los experimentos de ML."""
    try:
        client = MLClient()
        result = await client.get_experiments()
        return result
    except Exception as e:
        raise HTTPException(500, detail=f"Error al obtener experimentos: {str(e)}")


@router.get("/predictions")
async def get_predictions(
        zone_code: Optional[str] = None,
        current_user: User = Depends(get_current_user)
):
    """Obtiene predicciones realizadas."""
    try:
        client = MLClient()
        result = await client.get_predictions(zone_code)
        return result
    except Exception as e:
        raise HTTPException(500, detail=f"Error al obtener predicciones: {str(e)}")