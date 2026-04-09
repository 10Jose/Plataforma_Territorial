from fastapi import HTTPException, status


class IngestionException(HTTPException):
    """Base para excepciones del servicio."""
    pass


class FileTooLargeError(IngestionException):
    """Error: archivo excede tamaño máximo."""
    def __init__(self, max_size_mb: int):
        super().__init__(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"El archivo excede el tamaño máximo de {max_size_mb} MB"
        )


class InvalidFileFormatError(IngestionException):
    """Error: formato de archivo inválido."""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )


class FileEmptyError(IngestionException):
    """Error: archivo vacío."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo está vacío (0 bytes)"
        )


class TooManyRowsError(IngestionException):
    """Error: excede límite de filas."""
    def __init__(self, max_rows: int):
        super().__init__(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"El archivo excede el límite de {max_rows} filas"
        )


class DuplicateFileError(IngestionException):
    """Error: archivo duplicado (idempotencia)."""
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_200_OK,
            detail=message
        )