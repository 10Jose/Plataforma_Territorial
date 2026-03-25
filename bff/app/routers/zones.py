from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_zones():
    return {"zones": ["Usaquén", "Chapinero", "Suba"]}