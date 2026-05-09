from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database import get_db
from app.services.analytics_service import AnalyticsService
from app.services.indicators_service import IndicatorsService
from app.core.exceptions import AnalyticsException, NoDataError
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/training-data")
async def get_training_data(db: AsyncSession = Depends(get_db)):
    """Provee datos para entrenamiento de ML."""
    try:
        from app.domain.models import ZoneScore, ScaledZoneData
        from sqlalchemy import select

        # Obtener scores con contribuciones
        stmt = select(ZoneScore).order_by(ZoneScore.score_value.desc())
        result = await db.execute(stmt)
        scores = result.scalars().all()

        if not scores:
            raise HTTPException(404, detail="No hay datos de scoring disponibles")

        # Preparar features y target
        features = []
        target = []
        feature_names = ["population_contribution", "income_contribution", "education_contribution", "competition_penalty"]

        for score in scores:
            features.append([
                score.population_contribution or 0,
                score.income_contribution or 0,
                score.education_contribution or 0,
                score.competition_penalty or 0
            ])
            target.append(score.score_value or 0)

        return {
            "features": features,
            "target": target,
            "feature_names": feature_names,
            "target_name": "score",
            "samples_count": len(features)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error en GET /analytics/training-data")
        raise HTTPException(500, detail=f"Error interno: {str(e)}")