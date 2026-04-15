from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from typing import List, Dict, Optional
import logging
from app.domain.models import IndicatorResult
from app.domain.interfaces import ITransformationClient, ICompetitionClassifier
from app.services.transformation_client import TransformationClient
from app.services.competition_classifier import CompetitionClassifier
from app.core.exceptions import NoDataError

logger = logging.getLogger(__name__)


class IndicatorsService:

    def __init__(
            self,
            db: AsyncSession,
            transformation_client: Optional[ITransformationClient] = None,
            classifier: Optional[ICompetitionClassifier] = None
    ):
        """
        Args:
            db: Sesión de base de datos
            transformation_client: Cliente para ms-transformation (inyectado)
            classifier: Clasificador de competencia (inyectado)
        """
        self.db = db
        self.transformation_client = transformation_client or TransformationClient()
        self.classifier = classifier or CompetitionClassifier()

    def get_competition_level(self, value: float) -> str:

        return self.classifier.get_competition_level(value)

    async def _fetch_transformed_data(self) -> List[Dict]:
        """Obtiene datos transformados desde ms-transformation."""
        data = await self.transformation_client.get_zones_data()
        if not data:
            raise NoDataError()
        return data

    async def _save_indicators(self, transformation_run_id: int, indicators: List[Dict]) -> int:
        """Actualiza los indicadores en la base de datos."""
        count = 0
        for item in indicators:
            stmt = select(IndicatorResult).where(
                IndicatorResult.zone_code == item["zone_code"]
            )
            result = await self.db.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                existing.population_indicator = item["population"]
                existing.income_indicator = item["income"]
                existing.education_indicator = item["education"]
                existing.competition_indicator = item["competition"]
                existing.composite_indicator_json = item.get("composite", {})
                existing.calculated_at = func.now()
            else:
                record = IndicatorResult(
                    zone_code=item["zone_code"],
                    zone_name=item["zone_name"],
                    transformation_run_id=transformation_run_id,
                    population_indicator=item["population"],
                    income_indicator=item["income"],
                    education_indicator=item["education"],
                    competition_indicator=item["competition"],
                    composite_indicator_json=item.get("composite", {})
                )
                self.db.add(record)
            count += 1

        await self.db.commit()
        return count

    async def calculate_indicators(self) -> Dict:
        """Calcula indicadores para todas las zonas."""
        try:
            transformed_data = await self._fetch_transformed_data()
        except NoDataError:
            await self.db.execute(delete(IndicatorResult))
            await self.db.commit()
            logger.info("Indicadores eliminados porque no hay datos transformados")
            raise

        transformation_run_id = transformed_data[0].get("transformation_run_id") if transformed_data else None

        indicators = []
        for zone in transformed_data:
            competition_value = zone.get("other_variables_json", {}).get("negocios", 0)
            indicators.append({
                "zone_code": zone.get("zone_code", ""),
                "zone_name": zone.get("zone_name", ""),
                "population": zone.get("population_density", 0),
                "income": zone.get("average_income", 0),
                "education": zone.get("education_level", 0),
                "competition": competition_value,
                "competition_level": self.get_competition_level(competition_value),
                "composite": {
                    "population_raw": zone.get("population_density", 0),
                    "income_raw": zone.get("average_income", 0),
                    "education_raw": zone.get("education_level", 0),
                    "competition_raw": competition_value
                }
            })

        saved_count = await self._save_indicators(transformation_run_id, indicators)

        return {
            "status": "completed",
            "zones_processed": saved_count,
            "indicators": indicators
        }
