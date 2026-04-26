from fastapi import FastAPI
from app.routers import audit
from app.infrastructure.database import engine, Base
from app.domain import models

app = FastAPI(
    title="Audit Service",
    description="Servicio de auditoría y trazabilidad",
    version="1.0.0"
)

app.include_router(audit.router, prefix="/audit", tags=["Audit"])


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.on_event("startup")
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)