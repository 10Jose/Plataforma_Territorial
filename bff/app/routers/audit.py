from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from app.services.audit_client import AuditClient
from app.routers.auth import get_current_user
from app.domain.models import User

router = APIRouter()


class AuditEventResponse(BaseModel):
    id: int
    trace_id: str
    service_name: str
    event_type: str
    reference_id: Optional[str]
    user_id: Optional[int]
    username: Optional[str]
    details_json: Optional[dict]
    status: str
    created_at: datetime


class AuditStatsResponse(BaseModel):
    total_events: int
    by_service: Dict[str, int]
    by_type: Dict[str, int]


@router.get("/events", response_model=List[AuditEventResponse])
async def get_audit_events(
        service_name: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = Query(100, le=1000),
        offset: int = 0,
        current_user: User = Depends(get_current_user)
):
    """Consulta eventos de auditoría con filtros."""
    try:
        client = AuditClient()
        result = await client.get_events(service_name, event_type, limit, offset)
        return result
    except Exception as e:
        raise HTTPException(500, detail=f"Error al obtener eventos de auditoría: {str(e)}")


@router.get("/events/trace/{trace_id}", response_model=List[AuditEventResponse])
async def get_trace_events(
        trace_id: str,
        current_user: User = Depends(get_current_user)
):
    """Obtiene todos los eventos de una misma traza."""
    try:
        client = AuditClient()
        result = await client.get_trace(trace_id)
        return result
    except Exception as e:
        raise HTTPException(500, detail=f"Error al obtener traza: {str(e)}")


@router.get("/stats")
async def get_audit_stats(
        current_user: User = Depends(get_current_user)
):
    """Obtiene estadísticas de auditoría."""
    try:
        client = AuditClient()
        result = await client.get_stats()
        return result  # ✅ Sin response_model para evitar validación estricta
    except Exception as e:
        raise HTTPException(500, detail=f"Error al obtener estadísticas: {str(e)}")