from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from io import BytesIO
import httpx
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

@router.get("/combined/stats")
async def get_combined_stats(
        db: AsyncSession = Depends(get_db)
):
    """Obtiene estadísticas del IA."""
    try:
        # 1. Obtener todos los scores combinados
        service = ScoringService(db)
        scores = await service.get_scores()

        if not scores:
            return {
                "status": "no_data",
                "message": "No hay scores calculados"
            }

        # 2. Obtener todas las predicciones ML
        predictions_map = {}
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get("http://ms-ml:8000/ml/predictions")
                if response.status_code == 200:
                    predictions = response.json()
                    for p in predictions:
                        predictions_map[p["zone_code"]] = p
        except Exception:
            pass

        # 3. Calcular estadísticas
        total_zones = len(scores)
        zones_with_ia = 0
        zones_without_ia = 0
        improved = 0
        worsened = 0
        unchanged = 0
        differences = []
        confidences = {"Alta": 0, "Media": 0, "Baja": 0}

        for score in scores:
            zone_code = score.get("zone_code", "")
            score_real = score.get("score", 0)

            if zone_code in predictions_map:
                zones_with_ia += 1
                pred = predictions_map[zone_code]
                predicted = pred.get("prediction_value", 0)
                difference = round(score_real - predicted, 2)
                differences.append(abs(difference))

                # Clasificación del Score Real
                real_level = score.get("opportunity_level", "Baja")

                # Clasificación de la Predicción
                pred_level = pred.get("prediction_label", "Baja")

                # Comparar si cambió la clasificación
                if pred_level == "Alta" and real_level != "Alta":
                    improved += 1
                elif pred_level == "Baja" and real_level != "Baja":
                    worsened += 1
                elif real_level == "Media" and pred_level == "Media":
                    unchanged += 1
                elif real_level == "Alta" and pred_level == "Alta":
                    unchanged += 1
                elif real_level == "Baja" and pred_level == "Baja":
                    unchanged += 1
                else:
                    unchanged += 1

                # Contar confianzas
                diff = abs(difference)
                if diff < 10:
                    confidences["Alta"] += 1
                elif diff < 20:
                    confidences["Media"] += 1
                else:
                    confidences["Baja"] += 1
            else:
                zones_without_ia += 1

        # Calcular confianza promedio
        avg_diff = round(sum(differences) / len(differences), 2) if differences else 0
        avg_confidence = "Alta" if avg_diff < 10 else "Media" if avg_diff < 20 else "Baja"

        # Calcular cambios de clasificación
        total_with_ia = zones_with_ia if zones_with_ia > 0 else 1

        return {
            "total_zones": total_zones,
            "zones_with_ia": zones_with_ia,
            "zones_without_ia": zones_without_ia,
            "classification_changes": {
                "improved": improved,
                "worsened": worsened,
                "unchanged": unchanged
            },
            "confidence_distribution": confidences,
            "average_difference": avg_diff,
            "average_confidence": avg_confidence
        }

    except Exception as e:
        logger.exception("Error en GET /scoring/combined/stats")
        raise HTTPException(500, detail=f"Error interno: {str(e)}")

@router.get("/combined/{zone_code}")
async def get_combined_analysis(
        zone_code: str,
        db: AsyncSession = Depends(get_db)
):
    try:

        # 1. Obtener score real
        service = ScoringService(db)
        score_data = await service.get_score_details(zone_code)

        if not score_data:
            raise HTTPException(404, detail=f"Zona {zone_code} no encontrada")

        # 2. Obtener predicción ML SOLO SI YA EXISTE
        prediction_data = None
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"http://ms-ml:8000/ml/predictions",
                    params={"zone_code": zone_code}
                )
                if response.status_code == 200:
                    predictions = response.json()
                    if predictions and len(predictions) > 0:
                        prediction_data = predictions[0]
        except Exception:
            pass

        # 3. Construir respuesta combinada
        result = {
            "zone_code": zone_code,
            "zone_name": score_data.get("zone_name", ""),
            "score_real": score_data.get("score", 0),
            "opportunity_level": score_data.get("opportunity_level", "Baja"),
            "contributions": score_data.get("contributions", {}),
            "weights_used": score_data.get("weights_used", {})
        }

        if prediction_data:
            predicted = prediction_data.get("prediction_value", 0)
            score_combinado = round(
                (score_data.get("score", 0) * 0.6) + (predicted * 0.4), 2
            )

            result["score_combinado_ia"] = score_combinado
            result["prediction_ml"] = predicted
            result["prediction_label"] = prediction_data.get("prediction_label", "Sin clasificar")
            result["difference"] = round(score_data.get("score", 0) - predicted, 2)
            result["confidence"] = (
                "Alta" if abs(result["difference"]) < 10
                else "Media" if abs(result["difference"]) < 20
                else "Baja"
            )
            result["formula"] = "Score_Combinado_IA = (Score_Real × 0.6) + (Predicción_ML × 0.4)"

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error en GET /scoring/combined/{zone_code}")
        raise HTTPException(500, detail=f"Error interno: {str(e)}")


@router.get("/recommendations/{zone_code}")
async def get_zone_recommendations(
        zone_code: str,
        db: AsyncSession = Depends(get_db)
):
    """Genera recomendaciones explicadas por zona."""
    try:
        service = ScoringService(db)
        recommendations = await service.generate_recommendations(zone_code)
        return recommendations
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error en GET /scoring/recommendations/{zone_code}")
        raise HTTPException(500, detail=f"Error interno: {str(e)}")

@router.get("/recommendations/{zone_code}/pdf")
async def download_recommendations_pdf(
        zone_code: str,
        db: AsyncSession = Depends(get_db)
):
    """Descarga la guía de acción en formato PDF."""
    try:
        service = ScoringService(db)
        pdf_bytes = await service.generate_recommendations_pdf(zone_code)

        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=guia_accion_{zone_code}.pdf"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error en GET /scoring/recommendations/{zone_code}/pdf")
        raise HTTPException(500, detail=f"Error interno: {str(e)}")

