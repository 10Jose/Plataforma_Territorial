import pandas as pd
from typing import List, Dict, Any
from app.domain.interfaces import DataValidator, ValidationResult
from app.domain.validators import ValidationRulesEngine


class PandasDataValidator(DataValidator):
    """Implementación de validador usando pandas."""

    def __init__(self, rules_engine: ValidationRulesEngine = None):
        self.rules_engine = rules_engine or ValidationRulesEngine()

    def _validate_row(
            self,
            row: pd.Series,
            original_row: pd.Series,
            idx: int
    ) -> List[str]:
        """
        Valida una fila individual.

        Args:
            row: Fila ya convertida (con tipos)
            original_row: Fila original (para mensajes)
            idx: Índice de la fila

        Returns:
            Lista de errores encontrados
        """
        row_errors = []

        # Validar zona (no nula ni vacía)
        if pd.isna(row['zona']) or str(row['zona']).strip() == '':
            row_errors.append("zona vacía o nula")

        # Validar columnas numéricas (poblacion, ingreso, negocios)
        for col in self.rules_engine.numeric_columns:
            val = row[col]
            original_val = original_row[col]

            if pd.isna(val):
                if not pd.isna(original_val) and str(original_val).strip() != '':
                    row_errors.append(f"{col} debe ser un número válido (valor: '{original_val}')")
                else:
                    row_errors.append(f"{col} nulo o vacío")
            elif val <= 0:
                row_errors.append(f"{col} debe ser positivo (valor: {val})")

        # Validar educación
        educ_val = row['educacion']
        original_educ = original_row['educacion']

        if pd.isna(educ_val):
            if not pd.isna(original_educ) and str(original_educ).strip() != '':
                row_errors.append(f"educacion no se pudo convertir a años (valor: '{original_educ}')")
            else:
                row_errors.append("educacion nulo o vacío")
        elif educ_val < 0:
            row_errors.append(f"educacion debe ser positivo (valor: {educ_val})")

        return row_errors

    def _prepare_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepara el DataFrame para validación (convierte tipos).

        Args:
            df: DataFrame original

        Returns:
            DataFrame con tipos convertidos
        """
        df_valid = df.copy()

        # Convertir columnas numéricas
        for col in self.rules_engine.numeric_columns:
            df_valid[col] = pd.to_numeric(df_valid[col], errors='coerce')

        # Convertir educación (texto a años)
        df_valid['educacion'] = df_valid['educacion'].apply(
            self.rules_engine.convert_education_to_years
        )

        return df_valid

    def validate(self, data: Any) -> ValidationResult:
        """
        Valida el dataset completo.

        Args:
            data: DataFrame a validar

        Returns:
            ValidationResult con contadores y errores
        """
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Se espera un DataFrame de pandas")

        df = data
        self.rules_engine.validate_columns(df)

        df_valid = self._prepare_dataframe(df)
        errors = []

        for idx, row in df_valid.iterrows():
            row_errors = self._validate_row(row, df.loc[idx], idx)
            if row_errors:
                errors.append({
                    "row": int(idx),
                    "row_data": df.loc[idx].to_dict(),
                    "errors": row_errors
                })

        valid_count = len(df) - len(errors)
        invalid_count = len(errors)

        return ValidationResult(
            valid_count=valid_count,
            invalid_count=invalid_count,
            errors=errors,
            rules_version=self.rules_engine.rules_version
        )