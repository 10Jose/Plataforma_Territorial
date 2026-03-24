from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Header
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database import get_db
from app.domain.models import DatasetLoad
import pandas as pd
import io

router = APIRouter()

@router.post("/load")
async def load_dataset(
        file: UploadFile = File(...),
        source_name: Optional[str] = None,
        source_type: Optional[str] = "CSV",
        uploaded_by: Optional[str] = Header(None, alias="X-User-Id"),  # si el frontend envía usuario
        db: AsyncSession = Depends(get_db)
):


    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail="Formato de archivo no válido. Solo se permiten archivos CSV."
        )

    # 2. Validar MIME type (opcional, pero buena práctica)
    if file.content_type not in ["text/csv", "application/vnd.ms-excel"]:
        raise HTTPException(
            status_code=400,
            detail="El archivo no parece ser CSV. Verifique el contenido."
        )

    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(
            status_code=400,
            detail="El archivo está vacío (0 bytes)."
        )


    # 1. Leer el CSV con Pandas
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading CSV: {str(e)}")

    # 2. Validación básica: al menos una columna, no vacío
    if df.empty:
        raise HTTPException(status_code=400, detail="Dataset is empty")

    total_rows = len(df)
    # Por ahora asumimos que todos son válidos; luego podrías implementar reglas
    valid_rows = total_rows
    invalid_rows = 0

    # 3. Crear registro en la base de datos
    dataset_load = DatasetLoad(
        file_name=file.filename,
        source_name=source_name,
        source_type=source_type,
        uploaded_by=uploaded_by,
        status="loaded",
        record_count=total_rows,
        valid_record_count=valid_rows,
        invalid_record_count=invalid_rows,
        metadata_json={
            "columns": list(df.columns),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()}
        }
    )
    db.add(dataset_load)
    await db.commit()
    await db.refresh(dataset_load)

    return {
        "id": dataset_load.id,
        "filename": file.filename,
        "rows": total_rows,
        "valid_rows": valid_rows,
        "invalid_rows": invalid_rows,
        "status": "loaded"
    }