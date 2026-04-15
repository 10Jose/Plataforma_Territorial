from fastapi import HTTPException, status

class AnalyticsException(HTTPException):
    pass

class NormalizationError(AnalyticsException):
    """Error durante la normalización."""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error de normalización: {detail}"
        )


class NoDataError(AnalyticsException):
    """Error: no hay datos para procesar."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay datos disponibles para el análisis"
        )

class ScalingError(AnalyticsException):
    """Error durante el reescalado."""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error de reescalado: {detail}"
        )
