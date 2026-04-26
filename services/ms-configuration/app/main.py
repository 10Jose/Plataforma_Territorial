from fastapi import FastAPI
from app.routers import configuration
from app.infrastructure.database import engine, Base
from app.domain import models

app = FastAPI(
    title="Configuration Service",
    description="Servicio de configuración de parámetros para scoring",
    version="1.0.0"
)

app.include_router(configuration.router, prefix="/configuration", tags=["Configuration"])


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.on_event("startup")
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)