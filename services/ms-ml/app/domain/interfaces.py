from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class TrainingData:
    """datos de entrenamiento."""
    features: list
    target: list
    feature_names: list
    target_name: str


@dataclass
class ModelInfo:
    """información del modelo."""
    id: int
    name: str
    version: str
    algorithm: str
    features_used: list
    target_variable: str
    evaluation_metric: str
    metric_value: float
    is_active: bool


@dataclass
class PredictionData:
    """resultado de predicción."""
    zone_code: str
    zone_name: str
    predicted_value: float
    confidence_score: Optional[float]
    model_version: str


class IModelTrainer(ABC):
    """Interfaz para entrenador de modelos."""

    @abstractmethod
    def train(self, features: list, target: list) -> Any:
        """Entrena un modelo."""
        pass

    @abstractmethod
    def predict(self, model: Any, features: list) -> list:
        """Realiza predicciones."""
        pass

    @abstractmethod
    def evaluate(self, model: Any, features: list, target: list) -> Dict[str, float]:
        """Evalúa el modelo."""
        pass

    @abstractmethod
    def get_algorithm_name(self) -> str:
        """Nombre del algoritmo."""
        pass


class IMLRepository(ABC):
    """Interfaz para repositorio de ML."""

    @abstractmethod
    async def save_experiment(self, experiment_data: Dict) -> int:
        """Guarda un experimento."""
        pass

    @abstractmethod
    async def save_model(self, model_data: Dict) -> int:
        """Guarda un modelo entrenado."""
        pass

    @abstractmethod
    async def save_prediction(self, prediction_data: Dict) -> None:
        """Guarda una predicción."""
        pass

    @abstractmethod
    async def get_active_model(self) -> Optional[Dict]:
        """Obtiene el modelo activo."""
        pass

    @abstractmethod
    async def get_experiments(self) -> list:
        """Obtiene todos los experimentos."""
        pass

    @abstractmethod
    async def get_predictions(self, zone_code: Optional[str] = None) -> list:
        """Obtiene predicciones."""
        pass