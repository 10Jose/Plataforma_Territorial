from typing import Dict, List, Optional
from app.domain.interfaces import ICompetitionClassifier
import logging
import numpy as np

logger = logging.getLogger(__name__)


class CompetitionClassifier(ICompetitionClassifier):

    def __init__(self, competition_values: Optional[List[float]] = None):
        """
        Args:
            competition_values: Lista de valores de competencia para calcular percentiles.
        """
        self._thresholds = None
        self._sorted_thresholds = None

        if competition_values and len(competition_values) >= 2:
            self._calculate_thresholds(competition_values)
        else:
            logger.warning("No hay suficientes datos para calcular umbrales de competencia")

    def _calculate_thresholds(self, values: List[float]) -> None:
        """Calcula umbrales basados en percentiles de los datos reales."""

        self._thresholds = {
            "Alta": float(np.percentile(values, 75)),
            "Media": float(np.percentile(values, 25)),
            "Baja": 0
        }

        self._sorted_thresholds = sorted(
            self._thresholds.items(),
            key=lambda x: -x[1]
        )

        logger.info(f"Umbrales calculados: Alta > {self._thresholds['Alta']:.0f}, "
                    f"Media > {self._thresholds['Media']:.0f}, Baja ≤ {self._thresholds['Media']:.0f}")

    def classify(self, value: float) -> str:
        """Clasifica el nivel de competencia según el valor numérico."""
        if self._sorted_thresholds is None:
            return "Sin datos"

        for level, threshold in self._sorted_thresholds:
            if value > threshold:
                return level
        return "Baja"

    def get_level(self, value: float) -> str:
        """Alias para compatibilidad con código existente."""
        return self.classify(value)

    def get_competition_level(self, value: float) -> str:
        """Alias adicional para máxima compatibilidad."""
        return self.classify(value)

    def get_thresholds(self) -> Optional[Dict[str, float]]:
        """Retorna los umbrales calculados."""
        return self._thresholds.copy() if self._thresholds else None