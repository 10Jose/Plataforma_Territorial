from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

from app.infrastructure.database import get_db
from app.repositories.audit_repository import AuditRepository
from app.services.audit_service import AuditService
from app.domain.interfaces import AuditEventData

router = APIRouter()


class AuditEventCreate(BaseModel):
    trace_id: str
    service_name: str
    event_type: str
    reference_id: Optional[str] = None
    user_id: Optional[int] = None
    username: Optional[str] = None
    details_json: Optional[dict] = None
    status: str = "success"


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


def get_audit_service(db: AsyncSession = Depends(get_db)) -> AuditService:
    repository = AuditRepository(db)
    return AuditService(repository)


@router.post("/events", status_code=201)
async def create_audit_event(
        event: AuditEventCreate,
        service: AuditService = Depends(get_audit_service)
):
    """Registra un evento de auditoría."""
    event_data = AuditEventData(
        trace_id=event.trace_id,
        service_name=event.service_name,
        event_type=event.event_type,
        reference_id=event.reference_id,
        user_id=event.user_id,
        username=event.username,
        details_json=event.details_json,
        status=event.status
    )
    result = await service.log_event(event_data)
    return {"id": result.id, "trace_id": result.trace_id}


@router.get("/events", response_model=List[AuditEventResponse])
async def get_audit_events(
        service_name: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = Query(100, le=1000),
        offset: int = 0,
        service: AuditService = Depends(get_audit_service)
):
    """Consulta eventos de auditoría con filtros."""
    events = await service.get_events(service_name, event_type, limit, offset)
    return events


@router.get("/events/trace/{trace_id}", response_model=List[AuditEventResponse])
async def get_trace_events(
        trace_id: str,
        service: AuditService = Depends(get_audit_service)
):
    """Obtiene todos los eventos de una misma traza."""
    return await service.get_trace(trace_id)


@router.get("/stats")
async def get_audit_stats(
        service: AuditService = Depends(get_audit_service)
):
    """Obtiene estadísticas de auditoría."""
    return await service.get_stats()