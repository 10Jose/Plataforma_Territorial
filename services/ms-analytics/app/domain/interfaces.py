from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
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

class IScoringFormula(ABC):
    @abstractmethod
    def calculate(
            self,
            population: float,
            income: float,
            education: float,
            competition: float,
            weights: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calcula el score y sus contribuciones.

        Returns:
            Diccionario con:
            - score: score final (0-100)
            - population_contribution
            - income_contribution
            - education_contribution
            - competition_penalty
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Nombre de la fórmula."""
        pass

    @abstractmethod
    def get_description(self) -> str:
        """Descripción de la fórmula."""
        pass


class IOpportunityClassifier(ABC):
    """Interfaz para clasificador de oportunidad."""

    @abstractmethod
    def classify(self, score: float) -> str:
        """Clasifica el nivel de oportunidad."""
        pass

    @abstractmethod
    def get_thresholds(self) -> Dict[str, float]:
        """Retorna los umbrales configurados."""
        pass


class IScoringRepository(ABC):
    """Interfaz para repositorio de scoring."""

    @abstractmethod
    async def save_execution(self, execution: Dict) -> int:
        """Guarda una ejecución y retorna su ID."""
        pass

    @abstractmethod
    async def save_scores(self, execution_id: int, scores: List[Dict]) -> int:
        """Guarda los scores calculados."""
        pass

    @abstractmethod
    async def update_execution_status(self, execution_id: int, status: str) -> None:
        """Actualiza el estado de una ejecución."""
        pass

    @abstractmethod
    async def get_latest_execution(self) -> Optional[Dict]:
        """Obtiene la última ejecución completada."""
        pass

    @abstractmethod
    async def get_scores(self, execution_id: int, zone_code: Optional[str] = None) -> List[Dict]:
        """Obtiene los scores de una ejecución."""
        pass

    @abstractmethod
    async def clear_all(self) -> None:
        """Limpia todas las tablas de scoring."""
        pass


class IScoringCalculator(ABC):
    """Interfaz para calculadora de scoring."""

    @abstractmethod
    async def calculate(self, scaled_data: List, weights: Dict[str, float]) -> List[Dict]:
        """Calcula scores para todas las zonas."""
        pass


@dataclass
class ZoneComparisonData:
    """datos de comparación de una zona."""
    zone_code: str
    zone_name: str
    score: float
    opportunity_level: str
    population_contribution: float
    income_contribution: float
    education_contribution: float
    competition_penalty: float
    population_scaled: float
    income_scaled: float
    education_scaled: float
    competition_scaled: float
    weights_used: Dict[str, float]


@dataclass
class ComparisonResult:
    """ resultado de comparación."""
    zones: List[ZoneComparisonData]
    metrics: List[str]
    best_values: Dict[str, Dict[str, Any]]
    radar_data: List[Dict[str, Any]]


class IZoneComparator(ABC):
    """Interfaz para comparador de zonas."""

    @abstractmethod
    async def compare(self, zone_codes: List[str]) -> ComparisonResult:
        """Compara múltiples zonas."""
        pass


class IComparisonFormatter(ABC):
    """Interfaz para formateador de comparación."""

    @abstractmethod
    def format_for_export(self, result: ComparisonResult) -> str:
        """Formatea para exportación (CSV/JSON)."""
        pass

    @abstractmethod
    def get_best_values(self, zones: List[ZoneComparisonData]) -> Dict[str, Dict[str, Any]]:
        """Identifica los mejores valores por métrica."""
        pass