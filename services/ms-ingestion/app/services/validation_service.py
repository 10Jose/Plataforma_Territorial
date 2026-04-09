from typing import Optional
import pandas as pd
from app.domain.interfaces import DataValidator, ValidationResult
from app.services.pandas_validator import PandasDataValidator


class ValidationService:

    def __init__(self, validator: Optional[DataValidator] = None):
        """
        Inicializa el servicio con un validador opcional.

        Args:
            validator: Implementación de DataValidator (por defecto usa PandasDataValidator)
        """
        self.validator = validator or PandasDataValidator()

    def validate_dataset(self, df: pd.DataFrame) -> ValidationResult:
        """
        Valida un dataset usando el validador inyectado.

        Args:
            df: DataFrame a validar

        Returns:
            ValidationResult con los resultados
        """
        return self.validator.validate(df)