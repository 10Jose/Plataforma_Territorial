from typing import List, Optional, Dict, Any
from app.domain.interfaces import IAuditRepository, AuditEventData


class AuditService:

    def __init__(self, repository: IAuditRepository):
        self.repository = repository

    async def log_event(self, event: AuditEventData) -> AuditEventData:
        """Registra un evento de auditoría."""
        return await self.repository.save(event)

    async def get_trace(self, trace_id: str) -> List[AuditEventData]:
        """Obtiene todos los eventos de una traza."""
        return await self.repository.find_by_trace_id(trace_id)

    async def get_events(
            self,
            service_name: Optional[str] = None,
            event_type: Optional[str] = None,
            limit: int = 100,
            offset: int = 0
    ) -> List[AuditEventData]:
        """Obtiene eventos con filtros."""
        return await self.repository.find_all(service_name, event_type, limit, offset)

    async def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de auditoría."""
        return {
            "total_events": await self.repository.count(),
            "by_service": await self.repository.count_by_service(),
            "by_type": await self.repository.count_by_type()
        }