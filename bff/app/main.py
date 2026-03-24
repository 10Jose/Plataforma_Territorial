from fastapi import FastAPI
from app.routers import zones, indicators, ranking, recommendations

app = FastAPI(title="BFF - Plataforma de Analítica Territorial")

app.include_router(zones.router, prefix="/api/zones", tags=["Zones"])
app.include_router(indicators.router, prefix="/api/indicators", tags=["Indicators"])
app.include_router(ranking.router, prefix="/api/ranking", tags=["Ranking"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["Recommendations"])

@app.get("/health")
def health():
    return {"status": "ok"}