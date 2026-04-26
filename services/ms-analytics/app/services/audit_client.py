import httpx
import os
import uuid
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class AuditClient:

    def __init__(self, service_name: str, base_url: Optional[str] = None):
        """
        Args:
            service_name: Nombre del servicio que envía eventos (ej: "ms-analytics")
            base_url: URL del servicio de auditoría
        """
        self.service_name = service_name
        self.base_url = base_url or os.getenv("AUDIT_SERVICE_URL", "http://ms-audit:8000")

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
        """
        Envía un evento de auditoría de forma asíncrona.

        Args:
            event_type: Tipo de evento (ej: "scoring_calculate_started")
            reference_id: ID de referencia (ej: execution_id)
            user_id: ID del usuario que ejecutó la acción
            username: Nombre del usuario
            details: Detalles adicionales en formato JSON
            status: "success" o "error"
            trace_id: ID de trazabilidad (si no se proporciona, se genera uno nuevo)

        Returns:
            trace_id si se envió correctamente, None si hubo error
        """
        trace_id = trace_id or str(uuid.uuid4())

        payload = {
            "trace_id": trace_id,
            "service_name": self.service_name,
            "event_type": event_type,
            "reference_id": reference_id,
            "user_id": user_id,
            "username": username,
            "details_json": details,
            "status": status
        }

        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                response = await client.post(
                    f"{self.base_url}/audit/events",
                    json=payload
                )
                response.raise_for_status()
                logger.debug(f"Evento de auditoría enviado: {event_type} | trace_id: {trace_id}")
                return trace_id

        except httpx.TimeoutException:
            logger.warning(f"Timeout enviando evento de auditoría: {event_type}")
            return None
        except httpx.ConnectError:
            logger.warning(f"Error de conexión con ms-audit: {event_type}")
            return None
        except Exception as e:
            logger.error(f"Error enviando evento de auditoría: {e}")
            return None