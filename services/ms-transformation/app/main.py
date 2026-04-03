from fastapi import FastAPI
from app.routers import sync, zones
from app.infrastructure.database import engine, Base
from app.domain import models

app = FastAPI(title="Transformation Service")

app.include_router(sync.router, prefix="/sync", tags=["Sync"])
app.include_router(zones.router, prefix="/zones", tags=["Zones"])

@app.get("/health")
def health():
    return {"status": "ok"}

@app.on_event("startup")
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)