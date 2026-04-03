import httpx
import os

class TransformationClient:
    def __init__(self):
        self.base_url = os.getenv("TRANSFORMATION_SERVICE_URL", "http://ms-transformation:8000")

    async def get_zones(self, skip: int = 0, limit : int = 100):
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/zones/", params={"skip": skip, "limit": limit})
            response.raise_for_status()
            return response.json()


    async def sync_zones(self):
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/sync/zones")
            response.raise_for_status()
            return response.json()