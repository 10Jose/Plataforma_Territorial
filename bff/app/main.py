from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.routers import load
from app.routers import zones, indicators, ranking, recommendations
from app.routers import datasets
import httpx
import os
import logging
from app.routers import auth
from app.infrastructure.database import engine, Base
from app.domain import models

logger = logging.getLogger(__name__)

app = FastAPI(title="BFF - Plataforma de Analítica Territorial")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(datasets.router, prefix="/api/datasets", tags=["Datasets"])
app.include_router(load.router, prefix="/api/load", tags=["Load"])
app.include_router(zones.router, prefix="/api/zones", tags=["Zones"])
app.include_router(datasets.router, prefix="/api/datasets", tags=["Datasets"])
app.include_router(indicators.router, prefix="/api/indicators", tags=["Indicators"])
app.include_router(ranking.router, prefix="/api/ranking", tags=["Ranking"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["Recommendations"])


@app.get("/health")
async def health():
    """
    Endpoint de salud que verifica el estado de todos los microservicios.
    """
    status = {
        "status": "ok",
        "services": {},
        "timestamp": None
    }

    import time
    status["timestamp"] = time.time()

    # Todos los microservicios del proyecto
    services = {
        "ingestion": os.getenv("INGESTION_SERVICE_URL", "http://ms-ingestion:8000"),
        "transformation": os.getenv("TRANSFORMATION_SERVICE_URL", "http://ms-transformation:8000"),
        "analytics": os.getenv("ANALYTICS_SERVICE_URL", "http://ms-analytics:8000"),
        "ml": os.getenv("ML_SERVICE_URL", "http://ms-ml:8000"),
        "recommendations": os.getenv("RECOMMENDATIONS_SERVICE_URL", "http://ms-recommendations:8000"),
        "configuration": os.getenv("CONFIGURATION_SERVICE_URL", "http://ms-configuration:8000"),
        "audit": os.getenv("AUDIT_SERVICE_URL", "http://ms-audit:8000"),
    }

    any_degraded = False

    for name, url in services.items():
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{url}/health", timeout=5.0)
                if response.status_code == 200:
                    status["services"][name] = {
                        "status": "connected",
                        "response": response.json() if response.content else None
                    }
                else:
                    status["services"][name] = {
                        "status": "unhealthy",
                        "status_code": response.status_code
                    }
                    any_degraded = True
                    logger.warning(f"Servicio {name} respondió con estado {response.status_code}")
        except httpx.TimeoutException:
            status["services"][name] = {
                "status": "timeout",
                "error": "No respondió en 5 segundos"
            }
            any_degraded = True
            logger.warning(f"Timeout al conectar con {name}")
        except httpx.ConnectError:
            status["services"][name] = {
                "status": "disconnected",
                "error": "No se pudo conectar"
            }
            any_degraded = True
            logger.error(f"No se pudo conectar con {name}")
        except Exception as e:
            status["services"][name] = {
                "status": "error",
                "error": str(e)
            }
            any_degraded = True
            logger.error(f"Error al conectar con {name}: {e}")

    if any_degraded:
        status["status"] = "degraded"

    return status


@app.get("/health/summary")
async def health_summary():
    status = {"status": "ok", "services": {}}

    services = {
        "ingestion": os.getenv("INGESTION_SERVICE_URL", "http://ms-ingestion:8000"),
        "transformation": os.getenv("TRANSFORMATION_SERVICE_URL", "http://ms-transformation:8000"),
        "analytics": os.getenv("ANALYTICS_SERVICE_URL", "http://ms-analytics:8000"),
        "ml": os.getenv("ML_SERVICE_URL", "http://ms-ml:8000"),
        "recommendations": os.getenv("RECOMMENDATIONS_SERVICE_URL", "http://ms-recommendations:8000"),
        "configuration": os.getenv("CONFIGURATION_SERVICE_URL", "http://ms-configuration:8000"),
        "audit": os.getenv("AUDIT_SERVICE_URL", "http://ms-audit:8000"),
    }

    for name, url in services.items():
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{url}/health", timeout=3.0)
                status["services"][name] = "ok" if response.status_code == 200 else "error"
        except:
            status["services"][name] = "down"
            status["status"] = "degraded"

    return status


@app.get("/")
async def root():
    return {
        "message": "BFF - Plataforma Analítica Territorial",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "health_summary": "/health/summary",
            "auth_register": "/api/auth/register (POST)",
            "auth_token": "/api/auth/token (POST)",
            "auth_me": "/api/auth/me (GET)",
            "load": "/api/load (POST)",
            "zones": "/api/zones",
            "datasets": "/api/datasets",
            "indicators": "/api/indicators",
            "ranking": "/api/ranking",
            "recommendations": "/api/recommendations"
        }
    }

@app.on_event("startup")
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)