from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.infrastructure.database import get_db
from app.services.indicators_service import IndicatorsService
from app.core.exceptions import AnalyticsException, NoDataError
from app.domain.models import IndicatorResult
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/calculate")
async def calculate_indicators(db: AsyncSession = Depends(get_db)):
    try:
        service = IndicatorsService(db)
        result = await service.calculate_indicators()
        return result
    except NoDataError as e:
        raise e
    except AnalyticsException as e:
        raise e
    except Exception as e:
        logger.exception("Error en POST /calculate")
        raise HTTPException(500, detail=f"Error interno: {str(e)}")


@router.get("/")
async def get_indicators(
        db: AsyncSession = Depends(get_db),
        zone_code: Optional[str] = None
):
    try:
        service = IndicatorsService(db)

        query = select(IndicatorResult).order_by(IndicatorResult.zone_name)
        if zone_code:
            query = query.where(IndicatorResult.zone_code == zone_code)

        result = await db.execute(query)
        indicators = result.scalars().all()

        return [
            {
                "id": i.id,
                "zone_code": i.zone_code,
                "zone_name": i.zone_name,
                "population": i.population_indicator,
                "income": i.income_indicator,
                "education": i.education_indicator,
                "competition": i.competition_indicator,
                "competition_level": service.get_competition_level(i.competition_indicator),
                "calculated_at": i.calculated_at.isoformat() if i.calculated_at else None
            }
            for i in indicators
        ]
    except Exception as e:
        logger.exception("Error en GET /analytics/")
        raise HTTPException(500, detail=f"Error interno: {str(e)}")
