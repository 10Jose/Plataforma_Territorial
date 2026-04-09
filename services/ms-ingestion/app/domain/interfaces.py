from abc import ABC, abstractmethod
from typing import Any, List, Dict
from dataclasses import dataclass


@dataclass
class ValidationResult:
    valid_count: int
    invalid_count: int
    errors: List[Dict]
    rules_version: str

    @property
    def is_valid(self) -> bool:
        """Indica si el dataset es completamente válido."""
        return self.invalid_count == 0

    @property
    def is_partial(self) -> bool:
        """Indica si el dataset es parcialmente válido."""
        return 0 < self.invalid_count < self.valid_count + self.invalid_count


class DataValidator(ABC):
    @abstractmethod
    def validate(self, data: Any) -> ValidationResult:
        """Valida los datos y retorna un ValidationResult."""
        pass