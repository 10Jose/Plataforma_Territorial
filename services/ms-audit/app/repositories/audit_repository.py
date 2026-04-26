from typing import List, Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.domain.models import AuditEvent
from app.domain.interfaces import IAuditRepository, AuditEventData


class AuditRepository(IAuditRepository):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(self, event: AuditEventData) -> AuditEventData:
        """Guarda un evento de auditoría."""
        audit_event = AuditEvent(
            trace_id=event.trace_id,
            service_name=event.service_name,
            event_type=event.event_type,
            reference_id=event.reference_id,
            user_id=event.user_id,
            username=event.username,
            details_json=event.details_json,
            status=event.status
        )
        self.db.add(audit_event)
        await self.db.commit()
        await self.db.refresh(audit_event)
        return self._to_dto(audit_event)

    async def find_by_trace_id(self, trace_id: str) -> List[AuditEventData]:
        """Busca eventos por trace_id."""
        query = select(AuditEvent).where(
            AuditEvent.trace_id == trace_id
        ).order_by(AuditEvent.created_at)

        result = await self.db.execute(query)
        events = result.scalars().all()
        return [self._to_dto(e) for e in events]

    async def find_all(
            self,
            service_name: Optional[str] = None,
            event_type: Optional[str] = None,
            limit: int = 100,
            offset: int = 0
    ) -> List[AuditEventData]:
        """Busca eventos con filtros."""
        query = select(AuditEvent).order_by(desc(AuditEvent.created_at))

        if service_name:
            query = query.where(AuditEvent.service_name == service_name)
        if event_type:
            query = query.where(AuditEvent.event_type == event_type)

        query = query.limit(limit).offset(offset)
        result = await self.db.execute(query)
        events = result.scalars().all()
        return [self._to_dto(e) for e in events]

    async def count(self) -> int:
        """Cuenta total de eventos."""
        result = await self.db.execute(select(func.count()).select_from(AuditEvent))
        return result.scalar() or 0

    async def count_by_service(self) -> Dict[str, int]:
        """Cuenta eventos por servicio."""
        result = await self.db.execute(
            select(AuditEvent.service_name, func.count())
            .group_by(AuditEvent.service_name)
        )
        return {row[0]: row[1] for row in result.all()}

    async def count_by_type(self) -> Dict[str, int]:
        """Cuenta eventos por tipo."""
        result = await self.db.execute(
            select(AuditEvent.event_type, func.count())
            .group_by(AuditEvent.event_type)
        )
        return {row[0]: row[1] for row in result.all()}

    def _to_dto(self, event: AuditEvent) -> AuditEventData:
        return AuditEventData(
            id=event.id,
            trace_id=event.trace_id,
            service_name=event.service_name,
            event_type=event.event_type,
            reference_id=event.reference_id,
            user_id=event.user_id,
            username=event.username,
            details_json=event.details_json,
            status=event.status,
            created_at=event.created_at
        )