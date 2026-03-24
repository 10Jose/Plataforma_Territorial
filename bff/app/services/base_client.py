import httpx
from typing import Any, Dict

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