from fastapi import HTTPException, status


class ConfigurationException(HTTPException):
    pass


class ProfileNotFoundError(ConfigurationException):
    def __init__(self, profile_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Perfil {profile_id} no encontrado"
        )


class InvalidWeightsError(ConfigurationException):
    def __init__(self, errors: list):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Pesos inválidos: {', '.join(errors)}"
        )


class NoActiveProfileError(ConfigurationException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay perfil activo"
        )