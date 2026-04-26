from app.services.weight_validator import WeightValidator
from app.services.profile_service import ProfileService


def get_weight_validator() -> WeightValidator:
    return WeightValidator(
        required_variables=["population", "income", "education", "competition"]
    )


class ConfigurationClient:

    def __init__(self, base_url: str = "http://ms-configuration:8000"):
        self.base_url = base_url

    async def get_active_weights(self) -> dict:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/configuration/weights/active")
            response.raise_for_status()
            data = response.json()
            return data.get("weights", {})


def get_configuration_client() -> ConfigurationClient:
    import os
    base_url = os.getenv("CONFIGURATION_SERVICE_URL", "http://ms-configuration:8000")
    return ConfigurationClient(base_url)