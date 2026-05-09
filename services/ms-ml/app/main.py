from fastapi import FastAPI
from app.routers import ml
from app.infrastructure.database import engine, Base
from app.domain import models

app = FastAPI(
    title="ML Service",
    description="Servicio de Machine Learning para predicción territorial",
    version="1.0.0"
)

app.include_router(ml.router, prefix="/ml", tags=["ML"])


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.on_event("startup")
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)