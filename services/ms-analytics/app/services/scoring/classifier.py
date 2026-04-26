from typing import Dict
from app.domain.interfaces import IOpportunityClassifier


class ThresholdClassifier(IOpportunityClassifier):
    """Clasificador basado en umbrales configurables."""

    DEFAULT_THRESHOLDS = {
        "Alta": 70.0,
        "Media": 40.0,
        "Baja": 0.0
    }

    def __init__(self, thresholds: Dict[str, float] = None):
        self.thresholds = thresholds or self.DEFAULT_THRESHOLDS.copy()
        self._sorted_thresholds = sorted(
            self.thresholds.items(),
            key=lambda x: -x[1]
        )

    def classify(self, score: float) -> str:
        """Clasifica el nivel de oportunidad."""
        for level, threshold in self._sorted_thresholds:
            if score >= threshold:
                return level
        return "Baja"

    def get_thresholds(self) -> Dict[str, float]:
        return self.thresholds.copy()