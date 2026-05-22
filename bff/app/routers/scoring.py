from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from io import BytesIO
from app.services.scoring_client import ScoringClient
from app.routers.auth import get_current_user
from app.domain.models import User

router = APIRouter()


class ContributionSchema(BaseModel):
    population: float
    income: float
    education: float
    competition_penalty: float


class ScoreResponse(BaseModel):
    id: int
    zone_code: str
    zone_name: str
    score: float
    opportunity_level: str
    contributions: ContributionSchema
    weights_used: dict
    calculated_at: Optional[str]


class CalculateResponse(BaseModel):
    status: str
    execution_id: int
    zones_processed: int
    weights_used: dict

class CompareRequest(BaseModel):
    zone_codes: List[str]


@router.post("/calculate", response_model=CalculateResponse)
async def calculate_scores(
        current_user: User = Depends(get_current_user)
):
    """Calcula el scoring para todas las zonas."""
    try:
        client = ScoringClient()
        result = await client.calculate_scores(
            user_id=current_user.id,
            username=current_user.username
        )
        return result
    except Exception as e:
        raise HTTPException(500, detail=f"Error al calcular scoring: {str(e)}")


@router.get("/scores", response_model=List[ScoreResponse])
async def get_scores(
        zone_code: Optional[str] = None,
        current_user: User = Depends(get_current_user)
):
    """Obtiene los scores calculados."""
    try:
        client = ScoringClient()
        result = await client.get_scores(zone_code)
        return result
    except Exception as e:
        raise HTTPException(500, detail=f"Error al obtener scores: {str(e)}")


@router.get("/scores/{zone_code}", response_model=ScoreResponse)
async def get_score_details(
        zone_code: str,
        current_user: User = Depends(get_current_user)
):
    """Obtiene el detalle del score de una zona."""
    try:
        client = ScoringClient()
        result = await client.get_score_details(zone_code)
        return result
    except Exception as e:
        raise HTTPException(500, detail=f"Error al obtener detalle del score: {str(e)}")

@router.get("/ranking")
async def get_ranking(
        limit: Optional[int] = None,
        opportunity_level: Optional[str] = None,
        current_user: User = Depends(get_current_user)
):
    """Obtiene el ranking de zonas."""
    try:
        client = ScoringClient()
        result = await client.get_ranking(limit, opportunity_level)
        return result
    except Exception as e:
        raise HTTPException(500, detail=f"Error al obtener ranking: {str(e)}")


@router.post("/compare")
async def compare_zones(
        request: CompareRequest,
        current_user: User = Depends(get_current_user)
):
    """Compara múltiples zonas."""
    try:
        client = ScoringClient()
        result = await client.compare_zones(request.zone_codes)
        return result
    except Exception as e:
        raise HTTPException(500, detail=f"Error al comparar zonas: {str(e)}")

@router.get("/combined/{zone_code}")
async def get_combined_analysis(
        zone_code: str,
        current_user: User = Depends(get_current_user)
):
    """Análisis combinado: score real + predicción ML."""
    try:
        client = ScoringClient()
        result = await client.get_combined_analysis(zone_code)
        return result
    except Exception as e:
        raise HTTPException(500, detail=f"Error al obtener análisis combinado: {str(e)}")


@router.get("/combined/stats")
async def get_combined_stats(
        current_user: User = Depends(get_current_user)
):
    """Obtiene estadísticas del Score Combinado IA."""
    try:
        client = ScoringClient()
        result = await client.get_combined_stats()
        return result
    except Exception as e:
        raise HTTPException(500, detail=f"Error al obtener estadísticas IA: {str(e)}")

@router.get("/recommendations/{zone_code}")
async def get_zone_recommendations(
        zone_code: str,
        current_user: User = Depends(get_current_user)
):
    """Obtiene recomendaciones explicadas para una zona."""
    try:
        client = ScoringClient()
        result = await client.get_zone_recommendations(zone_code)
        return result
    except Exception as e:
        raise HTTPException(500, detail=f"Error al obtener recomendaciones: {str(e)}")

@router.get("/recommendations/{zone_code}/pdf")
async def download_recommendations_pdf(
        zone_code: str,
        current_user: User = Depends(get_current_user)
):
    """Descarga la guía de acción en PDF."""
    try:
        client = ScoringClient()
        pdf_bytes = await client.download_recommendations_pdf(zone_code)

        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=guia_accion_{zone_code}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(500, detail=f"Error al descargar PDF: {str(e)}")