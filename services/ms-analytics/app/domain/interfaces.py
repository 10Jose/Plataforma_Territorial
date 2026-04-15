from abc import ABC, abstractmethod
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class ScalingResult:
    """Resultado del proceso de reescalado."""
    scaled_data: List[Dict]
    statistics: Dict[str, Dict[str, float]]
    method: str
    zones_processed: int


class ScalerInterface(ABC):
    """Abstracción para reescaladores de datos."""

    @abstractmethod
    def scale(self, data: List[Dict]) -> ScalingResult:
        """Reescala los datos."""
        pass

class ITransformationClient(ABC):
    """Interfaz para cliente de transformación."""

    @abstractmethod
    async def get_zones_data(self) -> list:
        """Obtiene los datos transformados de las zonas."""
        pass


class ICompetitionClassifier(ABC):
    """Interfaz para clasificador de competencia."""

    @abstractmethod
    def classify(self, value: float) -> str:
        """Clasifica el nivel de competencia."""
        pass

    @abstractmethod
    def get_level(self, value: float) -> str:
        """Alias para compatibilidad con código existente."""
        pass


class IScalingExecutionService(ABC):
    """Interfaz para servicio de ejecuciones de scaling."""

    @abstractmethod
    async def create_execution(self, method: str) -> int:
        """Crea una nueva ejecución y retorna su ID."""
        pass

    @abstractmethod
    async def mark_completed(self, execution_id: int) -> None:
        """Marca una ejecución como completada."""
        pass

    @abstractmethod
    async def mark_failed(self, execution_id: int) -> None:
        """Marca una ejecución como fallida."""
        pass


class IScaledDataRepository(ABC):
    """Interfaz para repositorio de datos reescalados."""

    @abstractmethod
    async def save(self, scaling_execution_id: int, scaled_data: list) -> int:
        """Guarda datos reescalados y retorna cantidad guardada."""
        pass