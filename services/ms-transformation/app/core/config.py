import os
from dataclasses import dataclass, field
from typing import Dict
from dotenv import load_dotenv

load_dotenv()


@dataclass
class TransformationRulesConfig:
    """Configuración de reglas de transformación."""
    education_mapping: Dict[str, int]
    rules_version: str
    rules_applied: str


@dataclass
class Settings:
    """Configuración principal del servicio."""

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://transform_user:transform_pass@db-transformation:5432/transform_db"
    )

    # Service URLs
    INGESTION_SERVICE_URL: str = os.getenv("INGESTION_SERVICE_URL", "http://ms-ingestion:8000")

    # Transformation rules
    TRANSFORMATION_RULES: TransformationRulesConfig = field(default_factory=lambda: TransformationRulesConfig(
        education_mapping={
            "ninguna": 0, "ninguno": 0,
            "primaria": 5, "primaria incompleta": 3,
            "secundaria": 11, "secundaria incompleta": 8,
            "bachiller": 11, "bachillerato": 11,
            "tecnica": 14, "tecnólogo": 14, "tecnologo": 14,
            "universitaria": 16, "profesional": 16,
            "postgrado": 18, "maestría": 18,
            "doctorado": 20,
        },
        rules_version="1.0.0",
        rules_applied="extracción de zonas, normalización, prevención de duplicados (v1.0.0)"
    ))


settings = Settings()