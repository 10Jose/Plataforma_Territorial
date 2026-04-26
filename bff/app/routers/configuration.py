from fastapi import APIRouter, HTTPException, Depends
from app.services.configuration_client import ConfigurationClient
from app.routers.auth import get_current_user
from app.domain.models import User
import httpx

router = APIRouter()


@router.get("/profiles")
async def get_profiles(current_user: User = Depends(get_current_user)):
    try:
        client = ConfigurationClient()
        result = await client.get_profiles()
        return result
    except Exception as e:
        raise HTTPException(500, detail=f"Error al obtener perfiles: {str(e)}")


@router.get("/profiles/active")
async def get_active_profile(current_user: User = Depends(get_current_user)):
    try:
        client = ConfigurationClient()
        result = await client.get_active_profile()
        return result
    except Exception as e:
        raise HTTPException(500, detail=f"Error al obtener perfil activo: {str(e)}")


@router.post("/profiles")
async def create_profile(data: dict, current_user: User = Depends(get_current_user)):
    try:
        client = ConfigurationClient()
        result = await client.create_profile(data)
        return result
    except Exception as e:
        raise HTTPException(500, detail=f"Error al crear perfil: {str(e)}")


@router.put("/profiles/{profile_id}")
async def update_profile(profile_id: int, data: dict, current_user: User = Depends(get_current_user)):
    try:
        client = ConfigurationClient()
        result = await client.update_profile(profile_id, data)
        return result
    except Exception as e:
        raise HTTPException(500, detail=f"Error al actualizar perfil: {str(e)}")


@router.post("/profiles/{profile_id}/activate")
async def activate_profile(profile_id: int, current_user: User = Depends(get_current_user)):
    try:
        client = ConfigurationClient()
        result = await client.activate_profile(profile_id)
        return result
    except Exception as e:
        raise HTTPException(500, detail=f"Error al activar perfil: {str(e)}")

@router.delete("/profiles/{profile_id}")
async def delete_profile(profile_id: int, current_user: User = Depends(get_current_user)):
    try:
        client = ConfigurationClient()
        result = await client.delete_profile(profile_id)
        return result
    except Exception as e:
        raise HTTPException(500, detail=f"Error al eliminar perfil: {str(e)}")


@router.get("/weights/active")
async def get_active_weights(current_user: User = Depends(get_current_user)):
    try:
        client = ConfigurationClient()
        result = await client.get_active_weights()
        return result
    except Exception as e:
        raise HTTPException(500, detail=f"Error al obtener pesos activos: {str(e)}")

@router.get("/profiles/{profile_id}")
async def get_profile(profile_id: int, current_user: User = Depends(get_current_user)):
    """Obtiene un perfil específico por ID."""
    try:
        client = ConfigurationClient()
        result = await client.get_profile(profile_id)
        return result
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(404, detail=f"Perfil {profile_id} no encontrado")
        raise HTTPException(e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(500, detail=f"Error al obtener perfil: {str(e)}")