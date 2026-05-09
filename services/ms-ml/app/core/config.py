import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://ml_user:ml_pass@db-ml:5432/ml_db"
    )
    ANALYTICS_SERVICE_URL: str = os.getenv(
        "ANALYTICS_SERVICE_URL",
        "http://ms-analytics:8000"
    )
    API_VERSION: str = "1.0.0"


settings = Settings()