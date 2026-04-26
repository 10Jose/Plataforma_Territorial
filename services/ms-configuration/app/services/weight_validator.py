from typing import Dict, List
from app.domain.interfaces import IWeightValidator


class WeightValidator(IWeightValidator):

    def __init__(self, required_variables: List[str] = None):
        self.required_variables = required_variables or [
            "population", "income", "education", "competition"
        ]
        self._errors: List[str] = []

    def validate(self, weights: Dict[str, float]) -> bool:
        self._errors = []

        for var in self.required_variables:
            if var not in weights:
                self._errors.append(f"Falta la variable: {var}")

        if self._errors:
            return False

        total = 0.0
        for var, weight in weights.items():
            if weight < 0 or weight > 100:
                self._errors.append(f"'{var}' debe estar entre 0 y 100")
            total += weight

        if abs(total - 100.0) > 0.01:
            self._errors.append(f"La suma debe ser 100% (actual: {total:.1f}%)")

        return len(self._errors) == 0

    def get_errors(self) -> List[str]:
        return self._errors.copy()