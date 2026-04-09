import os
from dataclasses import dataclass, field
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()


@dataclass
class ValidationRulesConfig:
    """Configuración de reglas de validación externalizadas."""
    required_columns: List[str]
    rules_version: str
    numeric_columns: List[str]
    education_mapping: Dict[str, int]


@dataclass
class Settings:
    """Configuración principal del servicio."""

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://ingestion_user:ingestion_pass@db-ingestion:5432/ingestion_db"
    )

    # SLA limits
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", 25 * 1024 * 1024))
    MAX_ROWS: int = int(os.getenv("MAX_ROWS", 10000))
    TIMEOUT_SECONDS: int = int(os.getenv("TIMEOUT_SECONDS", 60))

    # Upload directory
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "/app/uploads")

    # Schema version
    SCHEMA_VERSION: str = "1.0.0"

    # Validation rules (externalizadas para cumplir OCP)
    VALIDATION_RULES: ValidationRulesConfig = field(default_factory=lambda: ValidationRulesConfig(
        required_columns=['zona', 'poblacion', 'ingreso', 'educacion', 'negocios'],
        rules_version="1.0.0",
        numeric_columns=['poblacion', 'ingreso', 'negocios'],
        education_mapping={
            "ninguna": 0, "ninguno": 0,
            "primaria": 5, "primaria incompleta": 3,
            "secundaria": 11, "secundaria incompleta": 8,
            "bachiller": 11, "bachillerato": 11,
            "tecnica": 14, "tecnólogo": 14, "tecnologo": 14,
            "universitaria": 16, "profesional": 16,
            "postgrado": 18, "maestría": 18,
            "doctorado": 20,
        }
    ))


settings = Settings()