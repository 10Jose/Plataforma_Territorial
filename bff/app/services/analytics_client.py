from typing import Optional

from app.services.base_client import BaseClient
import os

class AnalyticsClient(BaseClient):
    def __init__(self):
        base_url = os.getenv("ANALYTICS_SERVICE_URL", "http://ms-analytics:8000")
        super().__init__(base_url)

    async def get_ranking(self):
        return await self.get("/analytics/ranking")

    async def get_indicators(self, zone_code: str = None):
        """Obtiene indicadores, filtrados por zona."""
        if zone_code:
            return await self.get(f"/analytics/?zone_code={zone_code}")
        return await self.get("/analytics/")

    async def calculate_indicators(self, user_id: Optional[int] = None, username: Optional[str] = None):
        """Dispara el cálculo de indicadores."""
        payload = {}
        if user_id is not None:
            payload["user_id"] = user_id
        if username is not None:
            payload["username"] = username
        return await self.post("/analytics/calculate", payload if payload else None)

    async def run_scaling(self):
        return await self.post("/analytics/scale")