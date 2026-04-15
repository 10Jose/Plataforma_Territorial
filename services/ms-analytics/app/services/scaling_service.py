from typing import List, Dict, Optional
import logging

from app.domain.interfaces import ScalerInterface, ScalingResult
from app.domain.scaling_rules import ScalingRulesEngine
from app.core.config import settings
from app.core.exceptions import ScalingError

logger = logging.getLogger(__name__)


class DataScaler(ScalerInterface):
    """Implementación del reescalador de datos."""

    def __init__(self, rules_engine: Optional[ScalingRulesEngine] = None):
        """
        Args:
            rules_engine: Motor de reglas de reescalado (inyectado)
        """
        self.rules_engine = rules_engine or ScalingRulesEngine(
            method=settings.SCALING.method,
            feature_range=settings.SCALING.feature_range
        )

    # ... resto del código SIN CAMBIOS ...
    # (mantener exactamente igual los métodos _extract_columns, _apply_scaling, _build_result, scale)