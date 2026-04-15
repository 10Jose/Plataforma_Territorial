from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database import get_db
from app.services.sync_service import SyncService
from app.core.exceptions import TransformationException

router = APIRouter()

@router.post("/zones")
async def sync_zones(db: AsyncSession = Depends(get_db)):
    """
    Endpoint para sincronizar zonas desde ms-ingestion.
    """
    try:
        service = SyncService()
        result = await service.sync_zones(db)

        return {
            "message": "Sincronización completada",
            "dataset_id": None,
            "transformation_run_id": None,
            "zones_processed": len(result.zones_data),
            "inserted": result.inserted_count,
            "updated": result.updated_count,
            "rules_version": result.rules_version
        }
    except TransformationException as e:
        raise e
    except Exception as e:
        logger.exception("Error en sync_zones")
        raise HTTPException(500, detail=f"Error interno: {str(e)}")