from typing import Dict
from app.domain.interfaces import ICompetitionClassifier


class CompetitionClassifier(ICompetitionClassifier):
    """Clasificador de nivel de competencia basado en umbrales configurables."""

    DEFAULT_THRESHOLDS: Dict[str, float] = {
        "Alta": 400,
        "Media": 200,
        "Baja": 0
    }

    def __init__(self, thresholds: Dict[str, float] = None):
        """
        Args:
            thresholds: Diccionario con niveles y umbrales.
                       Ej: {"Alta": 400, "Media": 200, "Baja": 0}
        """
        self.thresholds = thresholds or self.DEFAULT_THRESHOLDS.copy()
        # Ordenar de mayor a menor para clasificación correcta
        self._sorted_thresholds = sorted(
            self.thresholds.items(),
            key=lambda x: -x[1]
        )

    def classify(self, value: float) -> str:
        """Clasifica el nivel de competencia según el valor numérico."""
        for level, threshold in self._sorted_thresholds:
            if value > threshold:
                return level
        return "Baja"  # Fallback

    def get_level(self, value: float) -> str:
        """Alias para compatibilidad con código existente."""
        return self.classify(value)

    def get_competition_level(self, value: float) -> str:
        """Alias adicional para máxima compatibilidad."""
        return self.classify(value)