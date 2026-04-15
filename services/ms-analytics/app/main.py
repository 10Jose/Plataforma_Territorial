from fastapi import FastAPI
from app.routers import scaling_router, indicators_router
from app.infrastructure.database import engine, Base
from app.domain import models

app = FastAPI(
    title="Analytics Service",
    description="Servicio de analítica y reescalado de datos territoriales",
    version="1.0.0"
)

app.include_router(scaling_router, prefix="/analytics", tags=["Analytics"])
app.include_router(indicators_router, prefix="/analytics", tags=["Analytics"])


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.on_event("startup")
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)