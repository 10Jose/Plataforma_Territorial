import pandas as pd
from app.core.config import settings
from app.core.exceptions import (
    InvalidFileFormatError,
    FileEmptyError,
    FileTooLargeError,
    TooManyRowsError
)


class FileValidator:
    """Servicio para validar aspectos del archivo no del contenido."""

    @staticmethod
    def validate_extension(filename: str) -> None:
        """Valida que el archivo tenga extensión .csv."""
        if not filename.lower().endswith('.csv'):
            raise InvalidFileFormatError(
                "Formato de archivo no válido. Solo se permiten archivos CSV."
            )

    @staticmethod
    def validate_content_type(content_type: str) -> None:
        """Valida que el MIME type sea correcto."""
        if content_type not in ["text/csv", "application/vnd.ms-excel"]:
            raise InvalidFileFormatError(
                "El archivo no parece ser CSV. Verifique el contenido."
            )

    @staticmethod
    def validate_not_empty(contents: bytes) -> None:
        """Valida que el archivo no esté vacío."""
        if len(contents) == 0:
            raise FileEmptyError()

    @staticmethod
    def validate_size(contents: bytes) -> None:
        """Valida que el archivo no exceda el tamaño máximo."""
        if len(contents) > settings.MAX_FILE_SIZE:
            max_size_mb = settings.MAX_FILE_SIZE // (1024 * 1024)
            raise FileTooLargeError(max_size_mb)

    @staticmethod
    def validate_rows_count(df: pd.DataFrame) -> None:
        """Valida que el número de filas no exceda el límite."""
        if len(df) > settings.MAX_ROWS:
            raise TooManyRowsError(settings.MAX_ROWS)

    @staticmethod
    def validate_not_empty_dataframe(df: pd.DataFrame) -> None:
        """Valida que el DataFrame tenga datos (no solo encabezado)."""
        if df.empty:
            raise InvalidFileFormatError(
                "El archivo CSV no contiene datos (solo encabezado o sin filas)."
            )