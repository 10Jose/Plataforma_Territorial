import pandas as pd
import io
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Tuple

from app.core.config import settings
from app.core.exceptions import (
    DatasetNotFoundError,
    DownloadError,
    CSVReadError,
    NoDataTransformedError
)
from app.domain.models import TransformationRun, TransformedZoneData
from app.domain.interfaces import TransformationResult
from app.services.ingestion_client import IngestionClient
from app.services.zone_transformer import ZoneTransformer
from app.domain.transformation_rules import TransformationRulesEngine

import logging

logger = logging.getLogger(__name__)


class SyncService:
    """Servicio de sincronización de zonas desde ms-ingestion."""

    def __init__(self):
        self.client = IngestionClient()
        self.transformer = ZoneTransformer()
        self.rules_engine = TransformationRulesEngine()

    async def _get_latest_dataset(self) -> Dict:
        """
        Obtiene el último dataset válido o parcial.

        Returns:
            Dataset más reciente

        Raises:
            DatasetNotFoundError: Si no hay datasets válidos
        """
        # Primero intentar con "valid"
        datasets = await self.client.get_datasets(limit=1, validation_status="valid")

        # Si no hay, intentar con "partial"
        if not datasets:
            datasets = await self.client.get_datasets(limit=1, validation_status="partial")

        if not datasets:
            raise DatasetNotFoundError()

        latest = datasets[0]
        logger.info(f"Dataset encontrado: ID={latest['id']}, archivo={latest['file_name']}, estado={latest.get('validation_status')}")
        return latest

    async def _download_and_read_csv(self, dataset_id: int) -> pd.DataFrame:
        """
        Descarga y lee el archivo CSV del dataset.

        Args:
            dataset_id: ID del dataset

        Returns:
            DataFrame con los datos

        Raises:
            DownloadError: Si falla la descarga
            CSVReadError: Si falla la lectura del CSV
        """
        try:
            file_content = await self.client.get_dataset_file(dataset_id)
            logger.info(f"Archivo descargado: {len(file_content)} bytes")
        except Exception as e:
            raise DownloadError(str(e))

        try:
            df = pd.read_csv(io.BytesIO(file_content))
            # Ordenar por índice para garantizar orden determinista
            df = df.sort_index().reset_index(drop=True)
            logger.info(f"CSV leído: {len(df)} filas, columnas: {list(df.columns)}")
            return df
        except Exception as e:
            raise CSVReadError(str(e))

    def _transform_dataframe(self, df: pd.DataFrame) -> List[Dict]:
        """
        Transforma todas las filas del DataFrame.

        Args:
            df: DataFrame a transformar

        Returns:
            Lista de zonas transformadas
        """
        zones_data = []
        for idx, row in df.iterrows():
            try:
                transformed = self.transformer.transform_row(row)
                if transformed is not None:
                    zones_data.append(transformed)
                else:
                    logger.info(f"Fila {idx} omitida por datos inválidos")
            except Exception as e:
                logger.warning(f"Error en fila {idx}: {e}")

        if not zones_data:
            raise NoDataTransformedError()

        return zones_data

    async def _persist_zones(
            self,
            db: AsyncSession,
            dataset_id: int,
            zones_data: List[Dict]
    ) -> Tuple[int, int]:
        """
        Persiste las zonas transformadas en la base de datos.

        Args:
            db: Sesión de base de datos
            dataset_id: ID del dataset
            zones_data: Lista de zonas transformadas

        Returns:
            Tupla (inserted_count, updated_count)
        """
        # Crear TransformationRun
        run = TransformationRun(
            dataset_load_id=dataset_id,
            status="completed",
            rules_applied=self.rules_engine.rules_applied,
            output_version=self.rules_engine.rules_version
        )
        db.add(run)
        await db.flush()

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
        return inserted_count, updated_count

    async def sync_zones(self, db: AsyncSession) -> TransformationResult:
        """
        Ejecuta la sincronización completa de zonas.

        Args:
            db: Sesión de base de datos

        Returns:
            TransformationResult con los resultados
        """
        # 1. Obtener el último dataset
        latest = await self._get_latest_dataset()

        # 2. Descargar y leer CSV
        df = await self._download_and_read_csv(latest["id"])

        # 3. Validar columnas requeridas
        required = ['zona', 'poblacion', 'ingreso', 'educacion']
        self.rules_engine.validate_required_columns(df, required)

        # 4. Transformar datos
        zones_data = self._transform_dataframe(df)

        # 5. Persistir en BD
        inserted_count, updated_count = await self._persist_zones(
            db, latest["id"], zones_data
        )

        return TransformationResult(
            zones_data=zones_data,
            inserted_count=inserted_count,
            updated_count=updated_count,
            rules_version=self.rules_engine.rules_version
        )