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

    async def calculate_indicators(self):
        """Dispara el cálculo de indicadores."""
        return await self.post("/analytics/calculate")