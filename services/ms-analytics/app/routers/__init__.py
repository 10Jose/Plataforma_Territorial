from app.routers.scaling import router as scaling_router
from app.routers.indicators import router as indicators_router
from app.routers.scoring import router as scoring_router

__all__ = ["scaling_router", "indicators_router"]