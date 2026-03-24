from fastapi import FastAPI
from app.routers import data
from app.infrastructure.database import engine, Base
from app.domain import models   # ← importa el módulo que contiene tus modelos

app = FastAPI(title="Data Ingestion Service")

app.include_router(data.router, prefix="/data", tags=["Data"])

@app.get("/health")
def health():
    return {"status": "ok"}

@app.on_event("startup")
async def init_db():
    async with engine.begin() as conn:
        # Ahora Base.metadata conoce los modelos porque se importaron
        await conn.run_sync(Base.metadata.create_all)