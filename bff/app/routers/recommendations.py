from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_recommendations():
    return [{"zone": "Suba", "recommendation": "Alta oportunidad"}]