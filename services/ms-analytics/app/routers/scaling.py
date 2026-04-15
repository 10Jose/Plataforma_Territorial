from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database import get_db
from app.services.analytics_service import AnalyticsService
from app.core.exceptions import AnalyticsException, NoDataError

router = APIRouter()


@router.post("/scale")
async def run_scaling(db: AsyncSession = Depends(get_db)):
    try:
        service = AnalyticsService(db)
        result = await service.run_scaling()
        return result
    except NoDataError as e:
        raise e
    except AnalyticsException as e:
        raise e
    except Exception as e:
        raise HTTPException(500, detail=f"Error interno: {str(e)}")
