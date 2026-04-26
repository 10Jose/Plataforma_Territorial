from app.services.base_client import BaseClient
import os

class ConfigurationClient(BaseClient):
    def __init__(self):
        base_url = os.getenv("CONFIGURATION_SERVICE_URL", "http://ms-configuration:8000")
        super().__init__(base_url)

    async def get_profiles(self):
        return await self.get("/configuration/profiles")

    async def get_active_profile(self):
        return await self.get("/configuration/profiles/active")

    async def create_profile(self, data):
        return await self.post("/configuration/profiles", data)

    async def update_profile(self, profile_id, data):
        return await self.put(f"/configuration/profiles/{profile_id}", data)

    async def activate_profile(self, profile_id):
        return await self.post(f"/configuration/profiles/{profile_id}/activate")

    async def get_active_weights(self):
        return await self.get("/configuration/weights/active")

    async def delete_profile(self, profile_id):
        return await self.delete(f"/configuration/profiles/{profile_id}")

    async def get_profile(self, profile_id: int):
        return await self.get(f"/configuration/profiles/{profile_id}")