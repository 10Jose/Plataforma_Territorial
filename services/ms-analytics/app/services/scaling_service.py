from typing import List, Dict, Optional
import logging

from app.domain.interfaces import ScalerInterface, ScalingResult
from app.domain.scaling_rules import ScalingRulesEngine
from app.core.config import settings
from app.core.exceptions import ScalingError

logger = logging.getLogger(__name__)


class DataScaler(ScalerInterface):
    """Implementación del reescalador de datos."""

    def __init__(self, rules_engine: Optional[ScalingRulesEngine] = None):
        """
        Args:
            rules_engine: Motor de reglas de reescalado (inyectado)
        """
        self.rules_engine = rules_engine or ScalingRulesEngine(
            method=settings.SCALING.method,
            feature_range=settings.SCALING.feature_range
        )

    def _extract_columns(self, data: List[Dict]) -> Dict[str, List[float]]:
        """
        Args:
            data: Lista de datos de zonas

        Returns:
            Diccionario con columnas y sus valores
        """
        return {
            "population": [z.get("population_density", 0) for z in data],
            "income": [z.get("average_income", 0) for z in data],
            "education": [z.get("education_level", 0) for z in data],
            "competition": [z.get("other_variables_json", {}).get("negocios", 0) for z in data]
        }

    def _apply_scaling(self, columns: Dict[str, List[float]]) -> Dict[str, List[float]]:
        """
        Args:
            columns: Diccionario con columnas y sus valores

        Returns:
            Diccionario con columnas reescaladas
        """
        scaled = {}

        for name, values in columns.items():
            try:
                scaled[name] = self.rules_engine.scale_column(values, name)
                logger.info(f"Columna {name} reescalada con método {self.rules_engine.method}")
            except Exception as e:
                raise ScalingError(f"Error reescalando columna {name}: {str(e)}")

        return scaled

    def _build_result(self, original_data: List[Dict], scaled_columns: Dict[str, List[float]]) -> List[Dict]:
        """
        Construye el resultado combinando datos originales y reescalados.

        Args:
            original_data: Datos originales
            scaled_columns: Columnas reescaladas

        Returns:
            Lista de diccionarios con datos reescalados
        """
        result = []

        for i, item in enumerate(original_data):
            result.append({
                "zone_code": item.get("zone_code", ""),
                "zone_name": item.get("zone_name", ""),
                "population_scaled": scaled_columns["population"][i],
                "income_scaled": scaled_columns["income"][i],
                "education_scaled": scaled_columns["education"][i],
                "competition_scaled": scaled_columns["competition"][i],
                "population_raw": item.get("population_density", 0),
                "income_raw": item.get("average_income", 0),
                "education_raw": item.get("education_level", 0),
                "competition_raw": item.get("other_variables_json", {}).get("negocios", 0)
            })

        return result

    def scale(self, data: List[Dict]) -> ScalingResult:
        """
        Reescala los datos completos.

        Args:
            data: Lista de datos de zonas

        Returns:
            ScalingResult con datos reescalados y estadísticas
        """
        if not data:
            raise ScalingError("No hay datos para reescalar")

        # Extraer columnas
        columns = self._extract_columns(data)

        # Aplicar reescalado
        scaled_columns = self._apply_scaling(columns)

        # Construir resultado
        scaled_data = self._build_result(data, scaled_columns)

        # Obtener estadísticas
        statistics = self.rules_engine.get_statistics()

        return ScalingResult(
            scaled_data=scaled_data,
            statistics=statistics,
            method=self.rules_engine.method,
            zones_processed=len(scaled_data)
        )
