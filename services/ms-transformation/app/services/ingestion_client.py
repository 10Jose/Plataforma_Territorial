from typing import Optional
import httpx
import os
import logging

logger = logging.getLogger(__name__)


class IngestionClient:

    def __init__(self):
        self.base_url = os.getenv("INGESTION_SERVICE_URL", "http://ms-ingestion:8000")

    async def get_datasets(
            self,
            skip: int = 0,
            limit: int = 100,
            validation_status: Optional[str] = None
    ) -> list:
        """
        Obtiene la lista de datasets cargados.

        Args:
            skip: Número de registros a saltar
            limit: Máximo de registros
            validation_status: Filtro por estado de validación

        Returns:
            Lista de datasets
        """
        params = {"skip": skip, "limit": limit}
        if validation_status:
            params["validation_status"] = validation_status

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/data/datasets",
                params=params
            )
            response.raise_for_status()
            return response.json()

    async def get_dataset_file(self, dataset_id: int) -> bytes:
        """
        Descarga el archivo CSV de un dataset.

        Args:
            dataset_id: ID del dataset

        Returns:
            Contenido del archivo en bytes
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/data/file/{dataset_id}")
            response.raise_for_status()
            return response.content