from app.services.base_client import BaseClient
import os
import httpx
from typing import Optional, List, Dict


class ScoringClient(BaseClient):
    def __init__(self):
        base_url = os.getenv("ANALYTICS_SERVICE_URL", "http://ms-analytics:8000")
        super().__init__(base_url)

    async def calculate_scores(self, user_id: Optional[int] = None, username: Optional[str] = None) -> Dict:
        """Dispara el cálculo de scoring."""
        payload = {}
        if user_id:
            payload["user_id"] = user_id
        if username:
            payload["username"] = username
        return await self.post("/scoring/calculate",  payload if payload else None)

    async def get_scores(self, zone_code: Optional[str] = None) -> List[Dict]:
        """Obtiene los scores calculados."""
        if zone_code:
            return await self.get(f"/scoring/scores/{zone_code}")
        return await self.get("/scoring/scores")

    async def get_score_details(self, zone_code: str) -> Dict:
        """Obtiene el detalle del score de una zona."""
        return await self.get(f"/scoring/scores/{zone_code}")

    async def get_ranking(self, limit: Optional[int] = None, opportunity_level: Optional[str] = None) -> List[Dict]:
        """Obtiene el ranking de zonas."""
        params = {}
        if limit:
            params["limit"] = limit
        if opportunity_level:
            params["opportunity_level"] = opportunity_level

        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        endpoint = f"/scoring/ranking?{query_string}" if query_string else "/scoring/ranking"

        return await self.get(endpoint)

    async def compare_zones(self, zone_codes: List[str]) -> Dict:
        """Compara múltiples zonas."""
        return await self.post("/scoring/compare", {"zone_codes": zone_codes})

    async def get_combined_analysis(self, zone_code: str) -> Dict:
        """Obtiene análisis combinado score + predicción."""
        return await self.get(f"/scoring/combined/{zone_code}")

    async def get_combined_stats(self) -> Dict:
        """Obtiene estadísticas del Score Combinado IA."""
        return await self.get("/scoring/combined/stats")

    async def get_zone_recommendations(self, zone_code: str) -> Dict:
        """Obtiene recomendaciones para una zona."""
        return await self.get(f"/scoring/recommendations/{zone_code}")

    async def download_recommendations_pdf(self, zone_code: str) -> bytes:
        """Descarga la guía de acción en PDF."""

    async def download_recommendations_pdf(self, zone_code: str) -> bytes:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{self.base_url}/scoring/recommendations/{zone_code}/pdf")
            response.raise_for_status()
            return response.content