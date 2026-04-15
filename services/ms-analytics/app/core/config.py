import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class ScalingConfig:
    """Configuración de reescalado."""
    method: str = "minmax"
    feature_range: tuple = (0, 1)


@dataclass
class Settings:
    """Configuración principal del servicio."""

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://analytics_user:analytics_pass@db-analytics:5432/analytics_db"
    )

    TRANSFORMATION_SERVICE_URL: str = os.getenv(
        "TRANSFORMATION_SERVICE_URL",
        "http://ms-transformation:8000"
    )

    # Usar default_factory para valores mutables
    SCALING: ScalingConfig = field(default_factory=ScalingConfig)
    API_VERSION: str = "1.0.0"


settings = Settings()