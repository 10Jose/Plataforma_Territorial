import httpx
import os
import logging
from typing import Optional
from app.domain.interfaces import ITransformationClient

logger = logging.getLogger(__name__)


class TransformationClient(ITransformationClient):

    def __init__(self, base_url: Optional[str] = None):

        self.base_url = base_url or os.getenv(
            "TRANSFORMATION_SERVICE_URL",
            "http://ms-transformation:8000"
        )

    async def get_zones_data(self) -> list:
        """
        Obtiene los datos transformados de las zonas.

        Returns:
            Lista de zonas con sus datos transformados
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/zones/data")
            response.raise_for_status()
            return response.json()
