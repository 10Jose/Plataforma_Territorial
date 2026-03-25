import httpx
import os
from fastapi import UploadFile, HTTPException
import logging

logger = logging.getLogger(__name__)

class IngestionClient:
    def __init__(self):
        self.base_url = os.getenv("INGESTION_SERVICE_URL", "http://ms-ingestion:8000")
        logger.info(f"Cliente de ingesta inicializado con URL: {self.base_url}")

    async def upload(self, file: UploadFile):
        logger.info(f"Procesando archivo: {file.filename}, tamaño: {file.size}")
        contents = await file.read()
        logger.info(f"Contenido leído: {len(contents)} bytes")

        async with httpx.AsyncClient() as client:
            try:
                files = {"file": (file.filename, contents, file.content_type)}
                logger.info(f"Enviando petición a {self.base_url}/data/load")
                response = await client.post(f"{self.base_url}/data/load", files=files)

                logger.info(f"Respuesta recibida - status: {response.status_code}")
                logger.info(f"Headers: {response.headers}")
                logger.info(f"Body: {response.text[:500]}")

                # Intentar obtener JSON de la respuesta (incluso en errores)
                try:
                    error_data = response.json()
                    logger.info(f"JSON parseado: {error_data}")
                except Exception as json_err:
                    logger.warning(f"No se pudo parsear JSON: {json_err}")
                    error_data = None

                # Si la respuesta es exitosa, devolver JSON
                if response.status_code < 400:
                    return response.json()

                # Extraer el mensaje de error
                if error_data and "detail" in error_data:
                    detail = error_data["detail"]
                elif error_data and "message" in error_data:
                    detail = error_data["message"]
                else:
                    detail = response.text or f"Error {response.status_code} del servicio de ingesta"

                logger.error(f"Error de ms-ingestion: {detail}")
                raise HTTPException(status_code=response.status_code, detail=detail)

            except httpx.RequestError as e:
                logger.error(f"Error de conexión con ms-ingestion: {str(e)}")
                raise HTTPException(status_code=503, detail=f"No se pudo conectar con el servicio de ingesta: {str(e)}")