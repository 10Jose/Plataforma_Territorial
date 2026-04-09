from abc import ABC, abstractmethod
from typing import Any, List, Dict
from dataclasses import dataclass


@dataclass
class TransformationResult:
    """Resultado de la transformación de datos."""
    zones_data: List[Dict]
    inserted_count: int
    updated_count: int
    rules_version: str


class ZoneTransformerInterface(ABC):
    """Abstracción para el transformador de zonas."""

    @abstractmethod
    def transform_row(self, row: Any) -> Dict | None:
        """Transforma una fila del CSV."""
        pass

    @abstractmethod
    def normalize_name(self, name: str) -> str:
        """Normaliza el nombre de una zona."""
        pass


class SyncServiceInterface(ABC):
    """Abstracción para el servicio de sincronización."""

    @abstractmethod
    async def sync_zones(self, db) -> TransformationResult:
        """Sincroniza zonas desde ms-ingestion."""
        pass