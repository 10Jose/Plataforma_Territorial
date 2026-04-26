import httpx
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)


class BaseClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def get(self, endpoint: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}{endpoint}")
            resp.raise_for_status()
            return resp.json()

    async def post(self, endpoint: str, data: Any = None) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{self.base_url}{endpoint}", json=data)
            resp.raise_for_status()
            return resp.json()

    async def put(self, endpoint: str, data: dict = None):
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{self.base_url}{endpoint}",
                json=data,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    async def delete(self, endpoint: str):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.base_url}{endpoint}",
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error en DELETE {endpoint}: {str(e)}")
            raise