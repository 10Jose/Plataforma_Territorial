from typing import List, Dict
import numpy as np


class ScalingRulesEngine:

    def __init__(self, method: str = "minmax", feature_range: tuple = (0, 1)):
        self.method = method
        self.feature_range = feature_range
        self._stats: Dict[str, Dict[str, float]] = {}

    def _minmax_scale(self, values: List[float], name: str) -> List[float]:
        """Reescalado min-max a rango [0, 1]."""
        if not values:
            return []

        min_val = min(values)
        max_val = max(values)

        self._stats[name] = {"min": min_val, "max": max_val}

        if max_val == min_val:
            return [0.5] * len(values)

        range_min, range_max = self.feature_range
        return [
            range_min + (x - min_val) * (range_max - range_min) / (max_val - min_val)
            for x in values
        ]

    def _zscore_scale(self, values: List[float], name: str) -> List[float]:
        """Reescalado Z-Score."""
        if not values:
            return []

        mean_val = np.mean(values)
        std_val = np.std(values)

        self._stats[name] = {"mean": mean_val, "std": std_val}

        if std_val == 0:
            return [0.0] * len(values)

        return [(x - mean_val) / std_val for x in values]

    def scale_column(self, values: List[float], name: str) -> List[float]:
        """
        Args:
            values: Lista de valores a reescalar
            name: Nombre de la columna para estadísticas

        Returns:
            Lista de valores reescalados
        """
        if self.method == "minmax":
            return self._minmax_scale(values, name)
        elif self.method == "zscore":
            return self._zscore_scale(values, name)
        else:
            raise ValueError(f"Método no soportado: {self.method}")

    def get_statistics(self) -> Dict:
        """Retorna las estadísticas del último reescalado."""
        return self._stats