from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.ingestion_client import IngestionClient
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    logger.info(f"Endpoint /api/load llamado con archivo: {file.filename}")
    try:
        client = IngestionClient()
        result = await client.upload(file)
        return result
    except HTTPException as e:
        logger.error(f"HTTPException: {e.status_code} - {e.detail}")
        raise
    except Exception as e:
        logger.exception("Error inesperado en upload_file")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")