from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_zones():
    # Aquí deberías llamar al microservicio de ingesta o transformación
    # para obtener la lista de zonas. Por ahora, devolvemos un mock.
    return {"zones": ["Usaquén", "Chapinero", "Suba"]}