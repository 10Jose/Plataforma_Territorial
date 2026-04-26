import httpx
import os
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class ConfigurationClient:
    """Cliente HTTP para ms-configuration."""

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or os.getenv(
            "CONFIGURATION_SERVICE_URL",
            "http://ms-configuration:8000"
        )

    async def get_active_weights(self) -> Dict[str, float]:

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                url = f"{self.base_url}/configuration/weights/active"
                logger.info(f"Consultando configuración: {url}")

                response = await client.get(url)
                response.raise_for_status()

                data = response.json()
                weights = data.get("weights", {})

                logger.info(f"Pesos obtenidos: {weights}")
                return weights

        except httpx.HTTPStatusError as e:
            logger.error(f"Error HTTP {e.response.status_code}: {e.response.text}")
            return {"population": 25, "income": 25, "education": 25, "competition": 25}
        except Exception as e:
            logger.error(f"Error conectando a ms-configuration: {str(e)}")
            return {"population": 25, "income": 25, "education": 25, "competition": 25}

    async def get_active_profile(self) -> Optional[Dict]:
        """
        Obtiene el perfil activo completo.

        Returns:
            Diccionario con datos del perfil
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                url = f"{self.base_url}/configuration/profiles/active"
                response = await client.get(url)

                if response.status_code == 404:
                    return None

                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"Error obteniendo perfil activo: {str(e)}")
            return None