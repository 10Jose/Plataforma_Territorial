from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database import get_db
from app.services.indicators_service import IndicatorsService
from app.services.analytics_service import AnalyticsService
from app.services.transformation_client import TransformationClient
from app.services.competition_classifier import CompetitionClassifier
from app.services.scaling_service import DataScaler
from app.services.scaling_execution_service import ScalingExecutionService
from app.services.scaled_data_repository import ScaledDataRepository


def get_transformation_client() -> TransformationClient:
    """Provee una instancia de TransformationClient."""
    return TransformationClient()


def get_competition_classifier() -> CompetitionClassifier:
    """Provee una instancia de CompetitionClassifier."""
    return CompetitionClassifier()


def get_data_scaler() -> DataScaler:
    """Provee una instancia de DataScaler."""
    return DataScaler()


def get_scaling_execution_service(db: AsyncSession) -> ScalingExecutionService:
    """Provee una instancia de ScalingExecutionService."""
    return ScalingExecutionService(db)


def get_scaled_data_repository(db: AsyncSession) -> ScaledDataRepository:
    """Provee una instancia de ScaledDataRepository."""
    return ScaledDataRepository(db)


async def get_indicators_service(
        db: AsyncSession = None
) -> IndicatorsService:
    """
    Provee una instancia de IndicatorsService con dependencias inyectadas.
    """
    pass


async def get_analytics_service(
        db: AsyncSession = None
) -> AnalyticsService:
    """
    Provee una instancia de AnalyticsService con dependencias inyectadas.
    """
    pass