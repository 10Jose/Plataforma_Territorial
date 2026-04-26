from fastapi import APIRouter, HTTPException, Depends
from app.services.analytics_client import AnalyticsClient
from app.routers.auth import get_current_user
from app.domain.models import User

router = APIRouter()

@router.post("/scale")
async def run_scaling(current_user: User = Depends(get_current_user)):
    try:
        client = AnalyticsClient()
        result = await client.run_scaling()
        return result
    except Exception as e:
        raise HTTPException(500, detail=f"Error al ejecutar scaling: {str(e)}")