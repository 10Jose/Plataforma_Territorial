from fastapi import APIRouter, HTTPException,Depends,Query
from fastapi.responses import Response
from app.services.ingestion_client import IngestionClient
from app.routers.auth import get_current_user
from app.domain.models import User
from typing import  Optional

router = APIRouter()

@router.get("/")
async def get_datasets(
        current_user: User = Depends(get_current_user),
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=500),
        validation_status: Optional[str] = None
):
    try:
        client = IngestionClient()
        datasets = await client.get_datasets(skip, limit, validation_status)
        return datasets
    except Exception as e:
        raise HTTPException(500, detail=str(e))


@router.get("/file/{dataset_id}")
async def download_dataset_file(
        dataset_id: int,
        current_user: User = Depends(get_current_user)
):
    try:
        client = IngestionClient()
        file_content, filename = await client.get_dataset_file(dataset_id)

        return Response(
            content=file_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, detail=f"Error al descargar archivo: {str(e)}")
