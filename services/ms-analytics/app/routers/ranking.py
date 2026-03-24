from fastapi import APIRouter

router = APIRouter()

@router.get("/ranking")
async def get_ranking():
    return [
        {"zone": "Suba", "score": 0.87, "level": "alta oportunidad"},
        {"zone": "Usaquén", "score": 0.81, "level": "alta oportunidad"},
    ]