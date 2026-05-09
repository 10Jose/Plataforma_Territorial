from app.services.base_client import BaseClient
import os
from typing import Optional, Dict, List


class MLClient(BaseClient):
    """Cliente HTTP para ms-ml."""

    def __init__(self):
        base_url = os.getenv("ML_SERVICE_URL", "http://ms-ml:8000")
        super().__init__(base_url)

    async def train_model(self, config: Optional[Dict] = None) -> Dict:
        """Entrena un modelo de ML."""
        return await self.post("/ml/train", config or {})

    async def predict_zone(self, zone_code: str) -> Dict:
        """Predice el potencial de una zona."""
        return await self.get(f"/ml/predict/{zone_code}")

    async def get_experiments(self) -> List[Dict]:
        """Obtiene todos los experimentos."""
        return await self.get("/ml/experiments")

    async def get_predictions(self, zone_code: Optional[str] = None) -> List[Dict]:
        """Obtiene predicciones realizadas."""
        if zone_code:
            return await self.get(f"/ml/predictions?zone_code={zone_code}")
        return await self.get("/ml/predictions")