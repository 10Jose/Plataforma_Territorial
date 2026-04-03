from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Header
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database import get_db
from app.domain.models import DatasetLoad, DatasetFileReference
import pandas as pd
from fastapi.responses import Response
import io
import math
import numpy as np
from sqlalchemy import select
import hashlib
import os
import uuid
import asyncio
import time
import logging
from app.domain.validators import validate_dataset

logger = logging.getLogger(__name__)
router = APIRouter()

# Constantes de SLA
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
MAX_ROWS = 10000
TIMEOUT_SECONDS = 60

SCHEMA_VERSION = "1.0.0"

def clean_nan(obj):
    """Reemplaza NaN por None recursivamente para que sea JSON válido."""
    if isinstance(obj, dict):
        return {k: clean_nan(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_nan(item) for item in obj]
    elif isinstance(obj, float) and math.isnan(obj):
        return None
    elif isinstance(obj, np.float64) and np.isnan(obj):
        return None
    else:
        return obj

@router.post("/load")
async def load_dataset(
        file: UploadFile = File(...),
        source_name: Optional[str] = None,
        source_type: Optional[str] = "CSV",
        uploaded_by: Optional[str] = Header(None, alias="X-User-Id"),
        db: AsyncSession = Depends(get_db)
):
    start_time = time.time()

    try:
        async with asyncio.timeout(TIMEOUT_SECONDS):
            # Validar extensión
            if not file.filename.lower().endswith('.csv'):
                raise HTTPException(400, detail="Formato de archivo no válido. Solo se permiten archivos CSV.")

            # Validar MIME type
            if file.content_type not in ["text/csv", "application/vnd.ms-excel"]:
                raise HTTPException(400, detail="El archivo no parece ser CSV. Verifique el contenido.")

            # Leer el contenido
            contents = await file.read()
            if len(contents) == 0:
                raise HTTPException(400, detail="El archivo está vacío (0 bytes).")

            # SLA: Límite de tamaño
            if len(contents) > MAX_FILE_SIZE:
                raise HTTPException(413, detail=f"El archivo excede el tamaño máximo de {MAX_FILE_SIZE // (1024*1024)} MB")

            # Calcular checksum
            checksum = hashlib.sha256(contents).hexdigest()

            # IDEMPOTENCIA
            existing_file = await db.execute(
                select(DatasetFileReference).where(DatasetFileReference.checksum == checksum)
            )
            existing_ref = existing_file.scalar_one_or_none()

            if existing_ref:
                existing_load = await db.execute(
                    select(DatasetLoad).where(DatasetLoad.id == existing_ref.dataset_load_id)
                )
                load_record = existing_load.scalar_one()
                return {
                    "id": load_record.id,
                    "filename": load_record.file_name,
                    "rows": load_record.record_count,
                    "valid_rows": load_record.valid_record_count,
                    "invalid_rows": load_record.invalid_record_count,
                    "status": "already_loaded",
                    "message": "El archivo ya había sido cargado previamente"
                }

            # Procesamiento del archivo CSV
            try:
                df = pd.read_csv(io.BytesIO(contents))
            except Exception as e:
                raise HTTPException(400, detail=f"Error reading CSV: {str(e)}")

            if df.empty:
                raise HTTPException(400, detail="El archivo CSV no contiene datos (solo encabezado o sin filas).")

            # SLA: Límite de número de filas
            if len(df) > MAX_ROWS:
                raise HTTPException(413, detail=f"El archivo excede el límite de {MAX_ROWS} filas")

            try:
                valid_rows, invalid_rows, errors, rules_version = validate_dataset(df)
            except ValueError as e:
                raise HTTPException(400, detail=str(e))

            total_rows = len(df)

            if invalid_rows == 0:
                validation_status = "valid"
            elif valid_rows == 0:
                validation_status = "invalid"
            else:
                validation_status = "partial"

            # Construir metadatos
            metadata = {
                "columns": list(df.columns),
                "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                "errors": errors,
                "validation_rules_version": rules_version
            }
            metadata_clean = clean_nan(metadata)
            errors_clean = clean_nan(errors)

            # Guardar el archivo con un nombre temporal (con permisos restringidos)
            upload_dir = "/app/uploads"
            os.makedirs(upload_dir, mode=0o750, exist_ok=True)  # permisos: rwxr-x---

            temp_id = uuid.uuid4().hex[:8]
            temp_file_path = os.path.join(upload_dir, f"temp_{temp_id}_{file.filename}")

            try:
                with open(temp_file_path, "wb") as f:
                    f.write(contents)
                # Establecer permisos del archivo
                os.chmod(temp_file_path, 0o640)  # rw-r-----
            except Exception as e:
                raise HTTPException(500, detail=f"Error al guardar archivo temporal: {str(e)}")

            # Crear registro en BD
            try:
                dataset_load = DatasetLoad(
                    file_name=file.filename,
                    source_name=source_name,
                    source_type=source_type,
                    uploaded_by=uploaded_by,
                    status="loaded",
                    validation_status=validation_status,
                    schema_version=SCHEMA_VERSION,
                    record_count=total_rows,
                    valid_record_count=valid_rows,
                    invalid_record_count=invalid_rows,
                    metadata_json=metadata_clean
                )
                db.add(dataset_load)
                await db.flush()  # Obtener ID

                # Renombrar archivo temporal al nombre definitivo
                final_file_path = os.path.join(upload_dir, f"{dataset_load.id}_{file.filename}")
                os.rename(temp_file_path, final_file_path)

                # Crear referencia en BD
                file_ref = DatasetFileReference(
                    dataset_load_id=dataset_load.id,
                    storage_path=final_file_path,
                    file_format="CSV",
                    checksum=checksum
                )
                db.add(file_ref)

                # Confirmar transacción
                await db.commit()
                await db.refresh(dataset_load)

            except Exception as e:
                # Si algo falla, limpiar el archivo temporal
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                await db.rollback()
                raise HTTPException(500, detail=f"Error al guardar en base de datos: {str(e)}")

            # Log de rendimiento
            elapsed = time.time() - start_time
            logger.info(f"Carga completada en {elapsed:.2f}s | Archivo: {file.filename} | Filas: {total_rows} | Válidas: {valid_rows} | Estado: {validation_status}")

            # Alerta si excede un umbral
            if elapsed > 30:
                logger.warning(f"SLA: Carga lenta ({elapsed:.2f}s) para {file.filename}")

            return {
                "id": dataset_load.id,
                "filename": file.filename,
                "rows": int(total_rows),
                "valid_rows": int(valid_rows),
                "invalid_rows": int(invalid_rows),
                "validation_status": validation_status,
                "errors": errors_clean,
                "status": "loaded",
                "processing_time_ms": int(elapsed * 1000)
            }

    except asyncio.TimeoutError:
        logger.error(f"Timeout en carga de {file.filename} después de {TIMEOUT_SECONDS}s")
        raise HTTPException(408, detail=f"La operación excedió el tiempo límite de {TIMEOUT_SECONDS} segundos")


@router.get("/datasets")
async def get_datasets(
        db: AsyncSession = Depends(get_db),
        skip: int = 0,
        limit: int = 100,
        validation_status : Optional[str] = None
):
    # Construir la consulta base
    query = select(DatasetLoad).order_by(DatasetLoad.uploaded_at.desc())

    if validation_status:
        query = query.where(DatasetLoad.validation_status == validation_status)

    # Aplicar paginación
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    datasets = result.scalars().all()

    return [
        {
            "id": ds.id,
            "file_name": ds.file_name,
            "source_name": ds.source_name,
            "source_type": ds.source_type,
            "uploaded_at": ds.uploaded_at.isoformat(),
            "uploaded_by": ds.uploaded_by,
            "status": ds.status,
            "validation_status": ds.validation_status,
            "schema_version": ds.schema_version,  # ← agregar schema_version
            "record_count": ds.record_count,
            "valid_record_count": ds.valid_record_count,
            "invalid_record_count": ds.invalid_record_count,
        }
        for ds in datasets
    ]


@router.get("/file/{dataset_id}")
async def get_dataset_file(
        dataset_id: int,
        db: AsyncSession = Depends(get_db)
):
    # Buscar la referencia del archivo
    result = await db.execute(
        select(DatasetFileReference).where(DatasetFileReference.dataset_load_id == dataset_id)
    )
    file_ref = result.scalar_one_or_none()
    if not file_ref:
        raise HTTPException(404, "Archivo no encontrado")

    # Leer el archivo del sistema
    try:
        with open(file_ref.storage_path, "rb") as f:
            content = f.read()
    except FileNotFoundError:
        raise HTTPException(404, "El archivo físico no existe")

    # VERIFICACIÓN DE INTEGRIDAD
    current_checksum = hashlib.sha256(content).hexdigest()
    if current_checksum != file_ref.checksum:
        logger.warning(f"Integridad comprometida: archivo {file_ref.storage_path} (checksum mismatch)")
        raise HTTPException(409, detail="El archivo ha sido modificado o está corrupto")

    # Devolver el archivo CSV
    return Response(
        content=content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={file_ref.storage_path.split('/')[-1]}"
        }
    )