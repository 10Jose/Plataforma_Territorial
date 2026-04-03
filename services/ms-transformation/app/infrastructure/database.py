import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://transform_user:transform_pass@db-transformation:5432/transform_db")

# Engine asíncrono
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Fábrica de sesiones asíncronas
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Base para los modelos
Base = declarative_base()

# Dependencia que inyecta una sesión en los endpoints
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session