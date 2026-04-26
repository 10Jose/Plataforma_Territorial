from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.services.comparison.comparator import ZoneComparator
import logging
import uuid
from app.domain.interfaces import (
    IScoringCalculator,
    IScoringRepository,
    IScoringFormula,
    IOpportunityClassifier,
    ComparisonResult
)
from app.services.configuration_client import ConfigurationClient
from app.services.scoring.calculator import ScoringCalculator
from app.services.scoring.repository import ScoringRepository
from app.services.analytics_service import AnalyticsService
from app.services.audit_client import AuditClient
from app.domain.models import IndicatorResult, ZoneScore

from app.core.exceptions import NoDataError

logger = logging.getLogger(__name__)


class ScoringService:

    def __init__(
            self,
            db: AsyncSession,
            calculator: Optional[IScoringCalculator] = None,
            repository: Optional[IScoringRepository] = None,
            config_client: Optional[ConfigurationClient] = None,
            audit_client: Optional[AuditClient] = None
    ):
        self.db = db
        self.calculator = calculator or ScoringCalculator()
        self.repository = repository or ScoringRepository(db)
        self.config_client = config_client or ConfigurationClient()
        self.audit_client = audit_client or AuditClient("ms-analytics")

    async def _get_active_weights(self) -> Dict[str, float]:
        """Obtiene los pesos activos."""
        try:
            return await self.config_client.get_active_weights()
        except Exception as e:
            logger.warning(f"Error obteniendo pesos, usando defaults: {e}")
            return {"population": 25, "income": 25, "education": 25, "competition": 25}

    async def calculate_scores(
            self,
            user_id: Optional[int] = None,
            username: Optional[str] = None
    ) -> Dict:
        """Calcula el scoring para todas las zonas."""
        trace_id = str(uuid.uuid4())

        await self.audit_client.log_event(
            event_type="scoring_calculate_started",
            user_id=user_id,
            username=username,
            trace_id=trace_id
        )

        try:
            # Verificar si hay datos reescalados
            scaled_data = await self.repository.get_scaled_data()

            # Si no hay datos reescalados, ejecutar scaling automáticamente
            if not scaled_data:
                logger.info("No hay datos reescalados. Ejecutando scaling automático...")

                await self.audit_client.log_event(
                    event_type="scaling_auto_triggered",
                    user_id=user_id,
                    username=username,
                    trace_id=trace_id,
                    details={"reason": "no_scaled_data"}
                )

                stmt = select(IndicatorResult).limit(1)
                result = await self.db.execute(stmt)
                has_indicators = result.scalar_one_or_none() is not None

                if not has_indicators:
                    await self.repository.clear_all()
                    raise NoDataError("No hay indicadores calculados. Ejecuta primero el cálculo de indicadores.")

                analytics_service = AnalyticsService(self.db)

                try:
                    scaling_result = await analytics_service.run_scaling()
                    logger.info(f"Scaling completado: {scaling_result['zones_processed']} zonas procesadas")
                except Exception as e:
                    logger.error(f"Error en scaling automático: {e}")
                    await self.repository.clear_all()
                    raise NoDataError(f"Error al ejecutar scaling: {str(e)}")

                # Obtener datos reescalados después del scaling
                scaled_data = await self.repository.get_scaled_data()

                if not scaled_data:
                    await self.repository.clear_all()
                    raise NoDataError("No se pudieron obtener datos reescalados después del scaling")

            await self.db.execute(delete(ZoneScore))
            await self.db.commit()
            logger.info("Scores anteriores eliminados")

            # Obtener pesos
            weights = await self._get_active_weights()

            await self.audit_client.log_event(
                event_type="weights_loaded",
                user_id=user_id,
                username=username,
                trace_id=trace_id,
                details={"weights": weights}
            )

            # Crear ejecución
            execution_id = await self.repository.save_execution({
                "weights": weights,
                "formula_version": "1.0.0"
            })

            # Calcular scores
            scores = await self.calculator.calculate(scaled_data, weights)

            # Guardar scores
            saved_count = await self.repository.save_scores(execution_id, scores)

            # Actualizar estado
            await self.repository.update_execution_status(execution_id, "completed")

            await self.audit_client.log_event(
                event_type="scoring_calculate_completed",
                reference_id=str(execution_id),
                user_id=user_id,
                username=username,
                trace_id=trace_id,
                details={
                    "zones_processed": saved_count,
                    "execution_id": execution_id
                }
            )

            return {
                "status": "completed",
                "execution_id": execution_id,
                "zones_processed": saved_count,
                "weights_used": weights,
                "scaling_executed": scaled_data is None,
                "trace_id": trace_id
            }

        except Exception as e:
            await self.audit_client.log_event(
                event_type="scoring_calculate_failed",
                user_id=user_id,
                username=username,
                trace_id=trace_id,
                status="error",
                details={"error": str(e)}
            )
            if 'execution_id' in locals():
                await self.repository.update_execution_status(execution_id, "failed")
            raise e

    async def get_scores(self, zone_code: Optional[str] = None) -> List[Dict]:
        """Obtiene los scores calculados."""
        execution = await self.repository.get_latest_execution()
        if not execution:
            return []

        scores = await self.repository.get_scores(execution["id"], zone_code)

        for score in scores:
            score["weights_used"] = execution["weights"]
            if score.get("calculated_at"):
                score["calculated_at"] = score["calculated_at"].isoformat()

        return scores

    async def get_score_details(self, zone_code: str) -> Optional[Dict]:
        """Obtiene el detalle del score de una zona."""
        scores = await self.get_scores(zone_code)
        return scores[0] if scores else None

    async def get_ranking(self, limit: Optional[int] = None, opportunity_level: Optional[str] = None) -> List[Dict]:
        """Obtiene el ranking de zonas ordenado por score."""
        execution = await self.repository.get_latest_execution()
        if not execution:
            return []

        scores = await self.repository.get_scores(execution["id"])

        if opportunity_level:
            scores = [s for s in scores if s.get("opportunity_level") == opportunity_level]

        if limit:
            scores = scores[:limit]

        for idx, score in enumerate(scores):
            score["rank_position"] = idx + 1
            score["weights_used"] = execution["weights"]
            if score.get("calculated_at"):
                score["calculated_at"] = score["calculated_at"].isoformat()

        return scores

    async def compare_zones(self, zone_codes: List[str]) -> ComparisonResult:
        """Compara múltiples zonas."""
        comparator = ZoneComparator(self.db)
        return await comparator.compare(zone_codes)