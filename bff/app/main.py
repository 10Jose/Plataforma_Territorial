from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.routers import load
from app.routers import zones, indicators, ranking, recommendations

app = FastAPI(title="BFF - Plataforma de Analítica Territorial")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(load.router, prefix="/api/load", tags=["Load"])
app.include_router(zones.router, prefix="/api/zones", tags=["Zones"])
app.include_router(indicators.router, prefix="/api/indicators", tags=["Indicators"])
app.include_router(ranking.router, prefix="/api/ranking", tags=["Ranking"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["Recommendations"])

@app.get("/health")
def health():
    return {"status": "ok"}