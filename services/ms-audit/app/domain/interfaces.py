from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class AuditEventData:
    id: Optional[int] = None
    trace_id: str = ""
    service_name: str = ""
    event_type: str = ""
    reference_id: Optional[str] = None
    user_id: Optional[int] = None
    username: Optional[str] = None
    details_json: Optional[Dict[str, Any]] = None
    status: str = "success"
    created_at: Optional[datetime] = None


class IAuditRepository(ABC):

    @abstractmethod
    async def save(self, event: AuditEventData) -> AuditEventData:
        """Guarda un evento de auditoría."""
        pass

    @abstractmethod
    async def find_by_trace_id(self, trace_id: str) -> List[AuditEventData]:
        """Busca eventos por trace_id."""
        pass

    @abstractmethod
    async def find_all(
            self,
            service_name: Optional[str] = None,
            event_type: Optional[str] = None,
            limit: int = 100,
            offset: int = 0
    ) -> List[AuditEventData]:
        """Busca eventos con filtros."""
        pass

    @abstractmethod
    async def count(self) -> int:
        """Cuenta total de eventos."""
        pass

    @abstractmethod
    async def count_by_service(self) -> Dict[str, int]:
        """Cuenta eventos por servicio."""
        pass

    @abstractmethod
    async def count_by_type(self) -> Dict[str, int]:
        """Cuenta eventos por tipo."""
        pass


class IAuditClient(ABC):
    @abstractmethod
    async def log_event(
            self,
            event_type: str,
            reference_id: Optional[str] = None,
            user_id: Optional[int] = None,
            username: Optional[str] = None,
            details: Optional[Dict[str, Any]] = None,
            status: str = "success",
            trace_id: Optional[str] = None
    ) -> Optional[str]:
        """Registra un evento de auditoría."""
        pass