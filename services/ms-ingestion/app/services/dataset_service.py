import hashlib
import os
import uuid
import pandas as pd
import io
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import DuplicateFileError
from app.domain.models import DatasetLoad, DatasetFileReference
from app.services.validation_service import ValidationService
from app.services.file_validator import FileValidator


class DatasetService:
    """Servicio principal para gestionar la carga de datasets."""

    def __init__(self, db: AsyncSession):
        """
        Inicializa el servicio con dependencias inyectadas.

        Args:
            db: Sesión asíncrona de base de datos
        """
        self.db = db
        self.validation_service = ValidationService()
        self.file_validator = FileValidator()

    async def _check_duplicate(self, checksum: str):
        """
        Verifica si ya existe un archivo con el mismo checksum.

        Args:
            checksum: SHA256 del archivo

        Returns:
            DatasetLoad existente o None
        """
        existing_file = await self.db.execute(
            select(DatasetFileReference).where(DatasetFileReference.checksum == checksum)
        )
        existing_ref = existing_file.scalar_one_or_none()

        if existing_ref:
            existing_load = await self.db.execute(
                select(DatasetLoad).where(DatasetLoad.id == existing_ref.dataset_load_id)
            )
            return existing_load.scalar_one()
        return None

    async def _save_file(self, contents: bytes, filename: str, dataset_id: int) -> str:
        """
        Guarda el archivo físicamente en el sistema.

        Args:
            contents: Contenido del archivo
            filename: Nombre original del archivo
            dataset_id: ID del dataset para nombrar el archivo

        Returns:
            Ruta final del archivo guardado
        """
        os.makedirs(settings.UPLOAD_DIR, mode=0o750, exist_ok=True)

        temp_id = uuid.uuid4().hex[:8]
        temp_path = os.path.join(settings.UPLOAD_DIR, f"temp_{temp_id}_{filename}")

        with open(temp_path, "wb") as f:
            f.write(contents)
        os.chmod(temp_path, 0o640)

        final_path = os.path.join(settings.UPLOAD_DIR, f"{dataset_id}_{filename}")
        os.rename(temp_path, final_path)
        return final_path

    async def _save_metadata(self, file: UploadFile, uploaded_by: str, total_rows: int, validation_result) -> DatasetLoad:
        """
        Guarda los metadatos del dataset en la base de datos.

        Args:
            file: Archivo subido
            uploaded_by: Usuario que realiza la carga
            total_rows: Número total de filas
            validation_result: Resultado de la validación

        Returns:
            DatasetLoad guardado
        """
        # Determinar estado de validación
        if validation_result.invalid_count == 0:
            validation_status = "valid"
        elif validation_result.valid_count == 0:
            validation_status = "invalid"
        else:
            validation_status = "partial"

        metadata = {
            "columns": [],
            "validation_rules_version": validation_result.rules_version
        }

        dataset_load = DatasetLoad(
            file_name=file.filename,
            source_name=None,
            source_type="CSV",
            uploaded_by=uploaded_by,
            status="loaded",
            validation_status=validation_status,
            schema_version=settings.SCHEMA_VERSION,
            record_count=total_rows,
            valid_record_count=validation_result.valid_count,
            invalid_record_count=validation_result.invalid_count,
            metadata_json=metadata
        )
        self.db.add(dataset_load)
        await self.db.flush()
        return dataset_load

    async def process_upload(
            self,
            file: UploadFile,
            uploaded_by: str | None
    ) -> dict:
        """
        Procesa la carga completa de un dataset.

        Args:
            file: Archivo subido
            uploaded_by: Usuario que realiza la carga

        Returns:
            Diccionario con el resultado de la carga
        """
        # 1. Validaciones iniciales del archivo
        self.file_validator.validate_extension(file.filename)
        self.file_validator.validate_content_type(file.content_type)

        contents = await file.read()
        self.file_validator.validate_not_empty(contents)
        self.file_validator.validate_size(contents)

        # 2. Calcular checksum
        checksum = hashlib.sha256(contents).hexdigest()

        # 3. Verificar duplicado (idempotencia)
        existing = await self._check_duplicate(checksum)
        if existing:
            return {
                "id": existing.id,
                "filename": existing.file_name,
                "rows": existing.record_count,
                "valid_rows": existing.valid_record_count,
                "invalid_rows": existing.invalid_record_count,
                "status": "already_loaded",
                "message": "El archivo ya había sido cargado previamente"
            }

        # 4. Leer y validar CSV
        df = pd.read_csv(io.BytesIO(contents))
        self.file_validator.validate_not_empty_dataframe(df)
        self.file_validator.validate_rows_count(df)

        # 5. Validar contenido
        validation_result = self.validation_service.validate_dataset(df)

        # 6. Guardar metadatos y archivo
        dataset_load = await self._save_metadata(file, uploaded_by, len(df), validation_result)
        file_path = await self._save_file(contents, file.filename, dataset_load.id)

        file_ref = DatasetFileReference(
            dataset_load_id=dataset_load.id,
            storage_path=file_path,
            file_format="CSV",
            checksum=checksum
        )
        self.db.add(file_ref)
        await self.db.commit()
        await self.db.refresh(dataset_load)

        # 7. Respuesta
        return {
            "id": dataset_load.id,
            "filename": file.filename,
            "rows": len(df),
            "valid_rows": validation_result.valid_count,
            "invalid_rows": validation_result.invalid_count,
            "validation_status": dataset_load.validation_status,
            "status": "loaded"
        }