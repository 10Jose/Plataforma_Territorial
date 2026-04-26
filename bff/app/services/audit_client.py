from app.services.base_client import BaseClient
import os
from typing import Optional, List, Dict


class AuditClient(BaseClient):

    def __init__(self):
        base_url = os.getenv("AUDIT_SERVICE_URL", "http://ms-audit:8000")
        super().__init__(base_url)

    async def get_events(
            self,
            service_name: Optional[str] = None,
            event_type: Optional[str] = None,
            limit: int = 100,
            offset: int = 0
    ) -> List[Dict]:
        """Obtiene eventos de auditoría con filtros."""
        params = []
        if service_name:
            params.append(f"service_name={service_name}")
        if event_type:
            params.append(f"event_type={event_type}")
        params.append(f"limit={limit}")
        params.append(f"offset={offset}")

        query_string = "&".join(params)
        endpoint = f"/audit/events?{query_string}" if query_string else "/audit/events"
        return await self._make_request("GET", endpoint)

    async def get_trace(self, trace_id: str) -> List[Dict]:
        """Obtiene todos los eventos de una traza."""
        return await self._make_request("GET", f"/audit/events/trace/{trace_id}")

    async def get_stats(self) -> Dict:
        """Obtiene estadísticas de auditoría."""
        return await self._make_request("GET", "/audit/stats")

    async def _make_request(self, method: str, endpoint: str):
        """Maneja las peticiones HTTP."""
        import httpx
        url = f"{self.base_url}{endpoint}"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                if method == "GET":
                    response = await client.get(url)
                else:
                    response = await client.post(url)
                response.raise_for_status()
                return response.json()
        except httpx.ConnectError:
            raise Exception(f"No se pudo conectar a ms-audit en {self.base_url}")
        except httpx.TimeoutException:
            raise Exception(f"Timeout conectando a ms-audit")
        except Exception as e:
            raise Exception(f"Error en petición a ms-audit: {str(e)}")