import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://audit_user:audit_pass@db-audit:5432/audit_db"
    )
    API_VERSION: str = "1.0.0"


settings = Settings()