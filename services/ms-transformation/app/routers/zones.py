from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.infrastructure.database import get_db
from app.domain.models import TransformedZoneData, TransformationRun
import time
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/")
async def get_zones(
        db: AsyncSession = Depends(get_db),
        skip: int = Query(0, ge=0, description="Número de registros a saltar"),
        limit: int = Query(100, ge=1, le=500, description="Número máximo de registros a retornar")
):
    """
    Obtiene la lista de zonas únicas disponibles con paginación.
    """
    start_time = time.time()

    # Consulta paginada de zonas
    result = await db.execute(
        select(TransformedZoneData.zone_code, TransformedZoneData.zone_name)
        .distinct()
        .order_by(TransformedZoneData.zone_name)
        .offset(skip)
        .limit(limit)
    )
    zones = [{"code": code, "name": name} for code, name in result.all()]

    # Total de zonas únicas
    total_result = await db.execute(
        select(func.count(TransformedZoneData.zone_name.distinct()))
    )
    total = total_result.scalar()

    elapsed = time.time() - start_time
    logger.info(f"GET /zones completado en {elapsed:.3f}s (skip={skip}, limit={limit}, total={total})")

    return {
        "zones": zones,
        "total": total,
        "skip": skip,
        "limit": limit,
        "next": f"/zones?skip={skip + limit}&limit={limit}" if skip + limit < total else None
    }

@router.get("/data")
async def get_zones_data(
        db: AsyncSession = Depends(get_db),
        run_id: int = Query(None, description="ID del transformation run (opcional)")
):
    """Devuelve datos completos de las zonas para análisis."""

    # Si no se especifica run_id, usar el último
    if run_id is None:
        latest_run = await db.execute(
            select(TransformationRun.id).order_by(desc(TransformationRun.id)).limit(1)
        )
        run_id = latest_run.scalar()
        if run_id is None:
            return []

    result = await db.execute(
        select(TransformedZoneData)
        .where(TransformedZoneData.transformation_run_id == run_id)
        .order_by(TransformedZoneData.zone_name)
    )
    zones = result.scalars().all()

    return [
        {
            "zone_code": z.zone_code,
            "zone_name": z.zone_name,
            "population_density": z.population_density,
            "average_income": z.average_income,
            "education_level": z.education_level,
            "economic_activity_index": z.economic_activity_index,
            "commercial_presence_index": z.commercial_presence_index,
            "other_variables_json": z.other_variables_json,
            "transformation_run_id": z.transformation_run_id
        }
        for z in zones
    ]