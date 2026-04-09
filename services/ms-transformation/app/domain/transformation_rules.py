from typing import Any, Dict
import pandas as pd
import unicodedata
from app.core.config import settings


class TransformationRulesEngine:

    def __init__(self, config=None):
        self.config = config or settings.TRANSFORMATION_RULES

    @property
    def education_mapping(self) -> Dict[str, int]:
        return self.config.education_mapping

    @property
    def rules_version(self) -> str:
        return self.config.rules_version

    @property
    def rules_applied(self) -> str:
        return self.config.rules_applied

    def convert_education_to_years(self, value: Any) -> float | None:
        """
        Convierte texto descriptivo a años de escolaridad.

        Args:
            value: Valor a convertir (puede ser número o texto)

        Returns:
            Años convertidos o None si no es válido
        """
        if value is None or pd.isna(value):
            return None

        # Si ya es número, usarlo directamente
        try:
            return float(value)
        except (ValueError, TypeError):
            pass

        text = str(value).lower().strip()
        return self.education_mapping.get(text, None)

    def normalize_zone_name(self, name: str) -> str:
        """
        Normaliza nombres de zonas: mayúsculas, sin tildes, sin espacios extras.

        Args:
            name: Nombre original de la zona

        Returns:
            Nombre normalizado
        """
        if not name or not isinstance(name, str):
            return ""

        name = name.upper()
        name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')
        name = ' '.join(name.split())
        return name

    def validate_required_columns(self, df: pd.DataFrame, required: list) -> None:
        """
        Valida que existan todas las columnas requeridas.

        Args:
            df: DataFrame a validar
            required: Lista de columnas requeridas

        Raises:
            MissingColumnsError: Si faltan columnas
        """
        missing = [col for col in required if col not in df.columns]
        if missing:
            from app.core.exceptions import MissingColumnsError
            raise MissingColumnsError(missing)