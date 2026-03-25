from fastapi import FastAPI

from routers import ranking# ← ¡CORREGIDO!

app = FastAPI(title="Analytics Service")

app.include_router(ranking.router, prefix="/analytics", tags=["Analytics"])

@app.get("/health")
def health():
    return {"status": "ok"}