from fastapi import APIRouter, HTTPException, Depends
from app.services.analytics_client import AnalyticsClient
from app.routers.auth import get_current_user
from app.domain.models import User
import httpx

router = APIRouter()


@router.get("/")
async def get_indicators(
        current_user: User = Depends(get_current_user),
        zone_code: str = None
):
    try:
        client = AnalyticsClient()
        result = await client.get_indicators(zone_code)
        return result
    except httpx.HTTPStatusError as e:
        # Reenviar el código de estado y mensaje original
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.text
        )

    except Exception as e:
        raise HTTPException(500, detail=f"Error al obtener indicadores: {str(e)}")


@router.post("/calculate")
async def calculate_indicators(
        current_user: User = Depends(get_current_user)
):
    try:
        client = AnalyticsClient()
        result = await client.calculate_indicators()
        return result

    except httpx.HTTPStatusError as e:
        # Capturar específicamente el 404 de "No hay datos"
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail="No hay datos disponibles. Carga un archivo CSV primero."
            )
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.text
        )
    except Exception as e:
        raise HTTPException(500, detail=f"Error al calcular indicadores: {str(e)}")