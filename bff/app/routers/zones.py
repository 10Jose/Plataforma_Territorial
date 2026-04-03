from fastapi import APIRouter, HTTPException, Query
from app.services.transformation_client import TransformationClient

router = APIRouter()

@router.get("/")
async def get_zones(skip: int = Query(0, ge=0),
                    limit: int = Query(100, ge=1, le=500)
):
    try:
        client = TransformationClient()
        result = await client.get_zones(skip, limit)
        return result
    except Exception as e:
        raise HTTPException(500, detail=f"Error al obtener zonas: {str(e)}")