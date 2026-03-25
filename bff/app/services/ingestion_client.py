import httpx
import os
from fastapi import UploadFile

class IngestionClient:
    def __init__(self):
        self.base_url = os.getenv("INGESTION_SERVICE_URL", "http://ms-ingestion:8000")

    async def upload(self, file: UploadFile):
        # Leer el contenido completo del archivo
        contents = await file.read()
        # Volver a posicionar el puntero (opcional, no necesario si ya no se usa file.file)
        # await file.seek(0)  # si necesitas volver a leer en otro lado

        async with httpx.AsyncClient() as client:
            # Enviar el archivo como bytes
            files = {"file": (file.filename, contents, file.content_type)}
            response = await client.post(f"{self.base_url}/data/load", files=files)
            response.raise_for_status()
            return response.json()