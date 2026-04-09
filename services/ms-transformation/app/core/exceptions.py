from fastapi import HTTPException, status

class TransformationException(HTTPException):
    """excepciones del servicio."""
    pass


class DatasetNotFoundError(TransformationException):
    """Error: no hay datasets válidos."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay datasets válidos o parcialmente válidos para sincronizar"
        )


class DownloadError(TransformationException):
    """Error: no se pudo descargar el archivo."""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al descargar archivo: {detail}"
        )


class CSVReadError(TransformationException):
    """Error: no se pudo leer el CSV."""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al leer CSV: {detail}"
        )


class MissingColumnsError(TransformationException):
    """Error: faltan columnas requeridas."""
    def __init__(self, missing: list):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Columnas faltantes: {missing}"
        )


class NoDataTransformedError(TransformationException):
    """Error: no se pudo transformar ninguna fila."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo transformar ninguna fila"
        )