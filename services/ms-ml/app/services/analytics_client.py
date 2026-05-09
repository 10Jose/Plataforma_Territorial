import httpx
import os
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class AnalyticsClient:
    """Cliente HTTP para ms-analytics."""

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or os.getenv(
            "ANALYTICS_SERVICE_URL",
            "http://ms-analytics:8000"
        )

    async def get_training_data(self) -> Dict:
        """Obtiene datos de entrenamiento desde ms-analytics."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.base_url}/analytics/training-data")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error obteniendo datos de entrenamiento: {e}")
            raise

    async def get_zone_data(self, zone_code: str) -> Dict:
        """Obtiene datos de una zona específica."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/scoring/scores/{zone_code}"
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error obteniendo datos de zona {zone_code}: {e}")
            raise