from typing import Any
import pandas as pd
from app.core.config import settings


class ValidationRulesEngine:

    def __init__(self, config=None):
        self.config = config or settings.VALIDATION_RULES

    @property
    def required_columns(self):
        return self.config.required_columns

    @property
    def rules_version(self):
        return self.config.rules_version

    @property
    def numeric_columns(self):
        return self.config.numeric_columns

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
        return self.config.education_mapping.get(text, None)

    def validate_columns(self, df: pd.DataFrame) -> None:
        """
        Valida que existan todas las columnas requeridas.
        
        Args:
            df: DataFrame a validar
            
        Raises:
            ValueError: Si faltan columnas requeridas
        """
        missing = set(self.required_columns) - set(df.columns)
        if missing:
            raise ValueError(f"Columnas faltantes: {missing}")