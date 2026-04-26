from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class BusinessProfileData:
    id: Optional[int]
    name: str
    description: str
    target_business_type: str
    is_active: bool
    weights: Dict[str, float]
    created_at: Optional[str] = None


class IWeightValidator(ABC):
    @abstractmethod
    def validate(self, weights: Dict[str, float]) -> bool:
        pass

    @abstractmethod
    def get_errors(self) -> List[str]:
        pass