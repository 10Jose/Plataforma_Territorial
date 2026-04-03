from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.services.ingestion_client import IngestionClient
from app.services.transformation_client import TransformationClient
from app.routers.auth import get_current_user
from app.domain.models import User
import logging
import asyncio

logger = logging.getLogger(__name__)

router = APIRouter()

async def sync_zones_background():
    """Sincroniza zonas en ms-transformation en segundo plano."""
    try:
        transformation_client = TransformationClient()
        result = await transformation_client.sync_zones()
        logger.info(f"Sincronización de zonas completada: {result}")
    except Exception as e:
        logger.error(f"Error en sincronización de zonas: {e}")

@router.post("/")
async def upload_file(
        file: UploadFile = File(...),
        current_user: User = Depends(get_current_user)  # ← corregido: current_user
):
    logger.info(f"Endpoint /api/load llamado por usuario: {current_user.username}")
    try:
        client = IngestionClient()
        result = await client.upload(file, uploaded_by=current_user.username)

        # Sincronización en segundo plano
        asyncio.create_task(sync_zones_background())

        return result
    except HTTPException as e:
        logger.error(f"HTTPException: {e.status_code} - {e.detail}")
        raise
    except Exception as e:
        logger.exception("Error inesperado en upload_file")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")