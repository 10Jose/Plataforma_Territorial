from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.infrastructure.database import get_db
from app.domain.models import TransformedZoneData
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

    start_time = time.time()

    # 1. Consulta paginada de zonas
    result = await db.execute(
        select(TransformedZoneData.zone_code, TransformedZoneData.zone_name)
        .distinct()
        .order_by(TransformedZoneData.zone_name)
        .offset(skip)
        .limit(limit)
    )
    zones = [{"code": code, "name": name} for code, name in result.all()]

    # 2. Obtener total de zonas únicas (para paginación)
    total_result = await db.execute(
        select(func.count(TransformedZoneData.zone_name.distinct()))
    )
    total = total_result.scalar()

    # 3. Log de rendimiento
    elapsed = time.time() - start_time
    logger.info(f"GET /zones completado en {elapsed:.3f}s (skip={skip}, limit={limit}, total={total})")

    # 4. Construir respuesta con metadatos de paginación
    return {
        "zones": zones,
        "total": total,
        "skip": skip,
        "limit": limit,
        "next": f"/zones?skip={skip + limit}&limit={limit}" if skip + limit < total else None
    }