from fastapi import APIRouter, HTTPException
from app.services.analytics_client import AnalyticsClient

router = APIRouter()

@router.get("/")
async def get_ranking():
    try:
        client = AnalyticsClient()
        ranking = await client.get_ranking()
        return ranking
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error contacting analytics service: {str(e)}")