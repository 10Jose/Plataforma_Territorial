from app.services.base_client import BaseClient
import os

class AnalyticsClient(BaseClient):
    def __init__(self):
        base_url = os.getenv("ANALYTICS_SERVICE_URL", "http://localhost:8003")
        super().__init__(base_url)

    async def get_ranking(self):
        return await self.get("/analytics/ranking")

    async def get_indicators(self, zone_id: str = None):
        if zone_id:
            return await self.get(f"/analytics/indicators/{zone_id}")
        return await self.get("/analytics/indicators")