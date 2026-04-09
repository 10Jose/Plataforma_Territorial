from fastapi import APIRouter, Depends, UploadFile, File, Header, HTTPException
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi.responses import Response
import hashlib
import os

from app.infrastructure.database import get_db
from app.domain.models import DatasetLoad, DatasetFileReference
from app.services.dataset_service import DatasetService
from app.core.exceptions import IngestionException

router = APIRouter()


@router.post("/load")
async def load_dataset(
        file: UploadFile = File(...),
        source_name: Optional[str] = None,
        source_type: Optional[str] = "CSV",
        uploaded_by: Optional[str] = Header(None, alias="X-User-Id"),
        db: AsyncSession = Depends(get_db)
):
    """
    Endpoint para cargar un archivo CSV.

    Args:
        file: Archivo CSV a cargar
        source_name: Nombre de la fuente (opcional)
        source_type: Tipo de fuente (por defecto "CSV")
        uploaded_by: Usuario que realiza la carga (desde header X-User-Id)
        db: Sesión de base de datos

    Returns:
        Resultado de la carga con ID y estadísticas
    """
    try:
        service = DatasetService(db)
        result = await service.process_upload(file, uploaded_by)
        return result
    except IngestionException as e:
        raise e
    except Exception as e:
        raise HTTPException(500, detail=f"Error interno: {str(e)}")


@router.get("/datasets")
async def get_datasets(
        db: AsyncSession = Depends(get_db),
        skip: int = 0,
        limit: int = 100,
        validation_status: Optional[str] = None
):
    """
    Consulta el historial de datasets cargados.

    Args:
        db: Sesión de base de datos
        skip: Número de registros a saltar (paginación)
        limit: Máximo de registros a retornar
        validation_status: Filtro por estado de validación (opcional)

    Returns:
        Lista de datasets
    """
    query = select(DatasetLoad).order_by(DatasetLoad.uploaded_at.desc())

    if validation_status:
        query = query.where(DatasetLoad.validation_status == validation_status)

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
            "schema_version": ds.schema_version,
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
    """
    Descarga el archivo original de un dataset.

    Args:
        dataset_id: ID del dataset
        db: Sesión de base de datos

    Returns:
        Archivo CSV como descarga
    """
    result = await db.execute(
        select(DatasetFileReference).where(DatasetFileReference.dataset_load_id == dataset_id)
    )
    file_ref = result.scalar_one_or_none()
    if not file_ref:
        raise HTTPException(404, "Archivo no encontrado")

    try:
        with open(file_ref.storage_path, "rb") as f:
            content = f.read()
    except FileNotFoundError:
        raise HTTPException(404, "El archivo físico no existe")

    # Verificar integridad
    current_checksum = hashlib.sha256(content).hexdigest()
    if current_checksum != file_ref.checksum:
        raise HTTPException(409, detail="El archivo ha sido modificado o está corrupto")

    return Response(
        content=content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={file_ref.storage_path.split('/')[-1]}"
        }
    )