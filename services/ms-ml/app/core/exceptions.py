from fastapi import HTTPException, status


class MLException(HTTPException):
    pass


class NoDataError(MLException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay datos disponibles para entrenar el modelo"
        )


class NoModelError(MLException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay un modelo entrenado. Entrena un modelo primero."
        )


class TrainingError(MLException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en entrenamiento: {detail}"
        )