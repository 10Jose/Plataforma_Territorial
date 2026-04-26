from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.interfaces import IZoneComparator, ComparisonResult, ZoneComparisonData
from app.services.scoring.repository import ScoringRepository


class ZoneComparator(IZoneComparator):
    """Comparador de zonas."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = ScoringRepository(db)

    async def compare(self, zone_codes: List[str]) -> ComparisonResult:
        """Compara múltiples zonas."""
        if len(zone_codes) < 2:
            raise ValueError("Se requieren al menos 2 zonas para comparar")
        if len(zone_codes) > 5:
            raise ValueError("Máximo 5 zonas para comparar")

        # Obtener datos de cada zona
        zones_data = []
        for zone_code in zone_codes:
            data = await self._get_zone_data(zone_code)
            if data:
                zones_data.append(data)

        if len(zones_data) < 2:
            raise ValueError("No se encontraron datos para todas las zonas solicitadas")

        # Identificar mejores valores
        best_values = self._find_best_values(zones_data)

        # Preparar datos para radar
        radar_data = self._prepare_radar_data(zones_data)

        return ComparisonResult(
            zones=zones_data,
            metrics=["population", "income", "education", "competition", "score"],
            best_values=best_values,
            radar_data=radar_data
        )

    async def _get_zone_data(self, zone_code: str) -> ZoneComparisonData:
        """Obtiene los datos de una zona específica."""
        execution = await self.repository.get_latest_execution()
        if not execution:
            return None

        scores = await self.repository.get_scores(execution["id"], zone_code)
        if not scores:
            return None

        score_data = scores[0]

        # Obtener datos reescalados
        scaled_data = await self.repository.get_scaled_data_by_zone(zone_code)

        return ZoneComparisonData(
            zone_code=zone_code,
            zone_name=score_data.get("zone_name", ""),
            score=score_data.get("score", 0),
            opportunity_level=score_data.get("opportunity_level", "Baja"),
            population_contribution=score_data.get("contributions", {}).get("population", 0),
            income_contribution=score_data.get("contributions", {}).get("income", 0),
            education_contribution=score_data.get("contributions", {}).get("education", 0),
            competition_penalty=score_data.get("contributions", {}).get("competition_penalty", 0),
            population_scaled=scaled_data.population_scaled if scaled_data else 0,
            income_scaled=scaled_data.income_scaled if scaled_data else 0,
            education_scaled=scaled_data.education_scaled if scaled_data else 0,
            competition_scaled=scaled_data.competition_scaled if scaled_data else 0,
            weights_used=execution.get("weights", {})
        )

    def _find_best_values(self, zones: List[ZoneComparisonData]) -> Dict[str, Dict[str, Any]]:
        """Encuentra el mejor valor para cada métrica."""
        return {
            "population": {
                "zone": max(zones, key=lambda z: z.population_contribution).zone_name,
                "value": max(z.population_contribution for z in zones)
            },
            "income": {
                "zone": max(zones, key=lambda z: z.income_contribution).zone_name,
                "value": max(z.income_contribution for z in zones)
            },
            "education": {
                "zone": max(zones, key=lambda z: z.education_contribution).zone_name,
                "value": max(z.education_contribution for z in zones)
            },
            "competition": {
                "zone": min(zones, key=lambda z: z.competition_penalty).zone_name,
                "value": min(z.competition_penalty for z in zones)
            },
            "score": {
                "zone": max(zones, key=lambda z: z.score).zone_name,
                "value": max(z.score for z in zones)
            }
        }

    def _prepare_radar_data(self, zones: List[ZoneComparisonData]) -> List[Dict[str, Any]]:
        """Prepara datos para gráfico de radar."""
        variables = ["population", "income", "education", "competition"]

        radar_data = []
        for variable in variables:
            entry = {"variable": variable.capitalize()}
            for zone in zones:
                if variable == "population":
                    entry[zone.zone_name] = zone.population_scaled
                elif variable == "income":
                    entry[zone.zone_name] = zone.income_scaled
                elif variable == "education":
                    entry[zone.zone_name] = zone.education_scaled
                elif variable == "competition":
                    entry[zone.zone_name] = 1 - zone.competition_scaled  # Invertir
            radar_data.append(entry)

        return radar_data