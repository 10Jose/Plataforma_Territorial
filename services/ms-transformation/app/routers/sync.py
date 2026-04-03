from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.infrastructure.database import get_db
from app.domain.models import TransformationRun, TransformedZoneData
from app.services.ingestion_client import IngestionClient
import pandas as pd
import io
import logging
import unicodedata

logger = logging.getLogger(__name__)
router = APIRouter()

# Constantes para reproducibilidad
RULES_VERSION = "1.0.0"
RULES_APPLIED = f"extracción de zonas, normalización, prevención de duplicados (v{RULES_VERSION})"


def convert_education_to_years(value):
    """Convierte texto descriptivo a años de escolaridad."""
    if value is None or pd.isna(value):
        return None

    try:
        return float(value)
    except (ValueError, TypeError):
        pass

    text = str(value).lower().strip()
    mapping = {
        "ninguna": 0, "ninguno": 0,
        "primaria": 5, "primaria incompleta": 3,
        "secundaria": 11, "secundaria incompleta": 8,
        "bachiller": 11, "bachillerato": 11,
        "tecnica": 14, "tecnólogo": 14, "tecnologo": 14,
        "universitaria": 16, "profesional": 16,
        "postgrado": 18, "maestría": 18,
        "doctorado": 20,
    }
    return mapping.get(text, None)


def normalize_zone_name(name: str) -> str:
    """Normaliza nombres de zonas: mayúsculas, sin tildes, sin espacios extras."""
    if not name or not isinstance(name, str):
        return ""
    name = name.upper()
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')
    name = ' '.join(name.split())
    return name


def transform_zone(row):
    """Transforma una fila del CSV en el formato de TransformedZoneData."""
    zone_name_raw = row["zona"]
    zone_name_normalized = normalize_zone_name(zone_name_raw)

    # Convertir educación
    educacion_raw = row.get("educacion")
    educacion_years = convert_education_to_years(educacion_raw)

    if educacion_years is None:
        logger.warning(f"Educación no válida en fila, omitiendo: {row.to_dict()}")
        return None

    # Manejo de negocios
    negocios_raw = row.get("negocios")
    if negocios_raw is None or pd.isna(negocios_raw) or str(negocios_raw).strip() == "":
        negocios = 0
    else:
        try:
            negocios = float(negocios_raw)
        except (ValueError, TypeError):
            negocios = 0

    return {
        "zone_code": str(row.get("codigo", row.get("zona_id", row.name))),
        "zone_name": zone_name_normalized,
        "population_density": float(row["poblacion"]),
        "average_income": float(row["ingreso"]),
        "education_level": educacion_years,
        "economic_activity_index": float(row.get("actividad_economica", 0.5)),
        "commercial_presence_index": float(row.get("presencia_comercial", 0.5)),
        "other_variables_json": {
            "raw_poblacion": row["poblacion"],
            "raw_ingreso": row["ingreso"],
            "raw_educacion": educacion_raw,
            "raw_zone_name": zone_name_raw,
            "negocios": negocios
        }
    }


@router.post("/zones")
async def sync_zones(db: AsyncSession = Depends(get_db)):
    client = IngestionClient()

    # 1. Obtener el último dataset válido o parcial
    try:
        datasets = await client.get_datasets(limit=1, validation_status="valid")

        if not datasets:
            datasets = await client.get_datasets(limit=1, validation_status="partial")

        if not datasets:
            raise HTTPException(404, "No hay datasets válidos o parcialmente válidos para sincronizar")
        latest = datasets[0]
        logger.info(f"Dataset encontrado: ID={latest['id']}, archivo={latest['file_name']}, estado={latest.get('validation_status')}")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(500, f"Error al obtener dataset: {str(e)}")

    # 2. Descargar archivo
    try:
        file_content = await client.get_dataset_file(latest["id"])
        logger.info(f"Archivo descargado: {len(file_content)} bytes")
    except Exception as e:
        raise HTTPException(500, f"Error al descargar archivo: {str(e)}")

    # 3. Leer CSV con orden determinista
    try:
        df = pd.read_csv(io.BytesIO(file_content))
        # Ordenar por índice para garantizar orden determinista
        df = df.sort_index().reset_index(drop=True)
        logger.info(f"CSV leído: {len(df)} filas, columnas: {list(df.columns)}")
    except Exception as e:
        raise HTTPException(500, f"Error al leer CSV: {str(e)}")

    # 4. Validar columnas requeridas
    required = ['zona', 'poblacion', 'ingreso', 'educacion']
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise HTTPException(400, f"Columnas faltantes: {missing}")

    # 5. Transformar datos (reproducibilidad garantizada por orden de iteración)
    zones_data = []
    for idx, row in df.iterrows():
        try:
            transformed = transform_zone(row)
            if transformed is not None:
                zones_data.append(transformed)
            else:
                logger.info(f"Fila {idx} omitida por datos inválidos")
        except Exception as e:
            logger.warning(f"Error en fila {idx}: {e}")

    if not zones_data:
        raise HTTPException(400, "No se pudo transformar ninguna fila")

    # 6. Crear TransformationRun con versión de reglas
    run = TransformationRun(
        dataset_load_id=latest["id"],
        status="completed",
        rules_applied=RULES_APPLIED,
        output_version=RULES_VERSION
    )
    db.add(run)
    await db.flush()

    # 7. Insertar o actualizar zonas
    inserted_count = 0
    updated_count = 0

    for zone in zones_data:
        result = await db.execute(
            select(TransformedZoneData).where(
                TransformedZoneData.zone_name == zone["zone_name"]
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            # Actualizar datos existentes
            existing.population_density = zone["population_density"]
            existing.average_income = zone["average_income"]
            existing.education_level = zone["education_level"]
            existing.economic_activity_index = zone["economic_activity_index"]
            existing.commercial_presence_index = zone["commercial_presence_index"]
            existing.other_variables_json = zone["other_variables_json"]
            updated_count += 1
            logger.info(f"Zona actualizada: {zone['zone_name']}")
        else:
            # Crear nuevo registro
            transformed = TransformedZoneData(
                transformation_run_id=run.id,
                zone_code=zone["zone_code"],
                zone_name=zone["zone_name"],
                population_density=zone["population_density"],
                average_income=zone["average_income"],
                education_level=zone["education_level"],
                economic_activity_index=zone["economic_activity_index"],
                commercial_presence_index=zone["commercial_presence_index"],
                other_variables_json=zone["other_variables_json"]
            )
            db.add(transformed)
            inserted_count += 1
            logger.info(f"Nueva zona insertada: {zone['zone_name']}")

    await db.commit()

    return {
        "message": "Sincronización completada",
        "dataset_id": latest["id"],
        "transformation_run_id": run.id,
        "zones_processed": len(zones_data),
        "inserted": inserted_count,
        "updated": updated_count,
        "rules_version": RULES_VERSION
    }