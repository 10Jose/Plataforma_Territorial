from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.ingestion_client import IngestionClient

router = APIRouter()

@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    try:
        client = IngestionClient()
        result = await client.upload(file)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))