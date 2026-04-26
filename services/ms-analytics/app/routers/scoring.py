from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from pydantic import BaseModel
from app.infrastructure.database import get_db
from app.services.scoring_service import ScoringService
from app.core.exceptions import NoDataError
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class ScoreResponse(BaseModel):
    id: int
    zone_code: str
    zone_name: str
    score: float
    opportunity_level: str
    contributions: dict
    weights_used: dict
    calculated_at: Optional[str]

class CalculateRequest(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None

class CompareRequest(BaseModel):
    zone_codes: List[str]

def get_scoring_service(db: AsyncSession = Depends(get_db)) -> ScoringService:
    """Inyección de dependencia (DIP)."""
    return ScoringService(db)


@router.post("/calculate")
async def calculate_scores(
        request: CalculateRequest,service: ScoringService = Depends(get_scoring_service)
):
    """Calcula el scoring para todas las zonas."""
    try:
        result = await service.calculate_scores(
            user_id=request.user_id,
            username=request.username
        )
        return result
    except NoDataError as e:
        raise HTTPException(404, detail=str(e))
    except Exception as e:
        logger.exception("Error en POST /scoring/calculate")
        raise HTTPException(500, detail=f"Error interno: {str(e)}")


@router.get("/scores", response_model=List[ScoreResponse])
async def get_scores(
        zone_code: Optional[str] = None,
        service: ScoringService = Depends(get_scoring_service)
):
    """Obtiene los scores calculados."""
    try:
        scores = await service.get_scores(zone_code)
        return scores
    except Exception as e:
        logger.exception("Error en GET /scoring/scores")
        raise HTTPException(500, detail=f"Error interno: {str(e)}")


@router.get("/scores/{zone_code}", response_model=ScoreResponse)
async def get_score_details(
        zone_code: str,
        service: ScoringService = Depends(get_scoring_service)
):
    """Obtiene el detalle del score de una zona."""
    try:
        score = await service.get_score_details(zone_code)
        if not score:
            raise HTTPException(404, detail=f"Zona {zone_code} no encontrada")
        return score
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error en GET /scoring/scores/{zone_code}")
        raise HTTPException(500, detail=f"Error interno: {str(e)}")

@router.get("/ranking")
async def get_ranking(
        limit: Optional[int] = None,
        opportunity_level: Optional[str] = None,
        service: ScoringService = Depends(get_scoring_service)
):
    """Obtiene el ranking de zonas ordenado por score."""
    try:
        ranking = await service.get_ranking(limit, opportunity_level)
        return ranking
    except Exception as e:
        logger.exception("Error en GET /scoring/ranking")
        raise HTTPException(500, detail=f"Error interno: {str(e)}")

@router.post("/compare")
async def compare_zones(
        request: CompareRequest,
        service: ScoringService = Depends(get_scoring_service)
):
    """Compara múltiples zonas."""
    try:
        result = await service.compare_zones(request.zone_codes)
        return result
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
    except Exception as e:
        logger.exception("Error en POST /scoring/compare")
        raise HTTPException(500, detail=f"Error interno: {str(e)}")