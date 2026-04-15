from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Optional
from app.domain.interfaces import (
    ITransformationClient,
    ScalerInterface,
    IScalingExecutionService,
    IScaledDataRepository
)
from app.services.transformation_client import TransformationClient
from app.services.scaling_service import DataScaler
from app.services.scaling_execution_service import ScalingExecutionService
from app.services.scaled_data_repository import ScaledDataRepository
from app.core.exceptions import NoDataError


class AnalyticsService:

    def __init__(
            self,
            db: AsyncSession,
            transformation_client: Optional[ITransformationClient] = None,
            scaler: Optional[ScalerInterface] = None,
            execution_service: Optional[IScalingExecutionService] = None,
            repository: Optional[IScaledDataRepository] = None
    ):
        """
        Args:
            db: Sesión de base de datos
            transformation_client: Cliente para ms-transformation
            scaler: Servicio de reescalado
            execution_service: Servicio de ejecuciones
            repository: Repositorio de datos reescalados
        """
        self.db = db
        self.transformation_client = transformation_client or TransformationClient()
        self.scaler = scaler or DataScaler()
        self.execution_service = execution_service or ScalingExecutionService(db)
        self.repository = repository or ScaledDataRepository(db)

    async def _fetch_transformed_data(self) -> list:
        """Obtiene datos transformados desde ms-transformation."""
        data = await self.transformation_client.get_zones_data()
        if not data:
            raise NoDataError()
        return data

    async def run_scaling(self) -> Dict:
        """
        Ejecuta el proceso completo de reescalado.

        Returns:
            Diccionario con resultados de la operación
        """
        # 1. Crear registro de ejecución
        execution_id = await self.execution_service.create_execution(
            self.scaler.rules_engine.method
        )

        try:
            # 2. Obtener datos transformados
            transformed_data = await self._fetch_transformed_data()

            # 3. Reescalar datos
            result = self.scaler.scale(transformed_data)

            # 4. Guardar datos reescalados
            saved_count = await self.repository.save(execution_id, result.scaled_data)

            # 5. Actualizar estado
            await self.execution_service.mark_completed(execution_id)

            return {
                "scaling_execution_id": execution_id,
                "status": "completed",
                "method": result.method,
                "zones_processed": saved_count,
                "statistics": result.statistics
            }

        except Exception as e:
            await self.execution_service.mark_failed(execution_id)
            raise e