import pandas as pd
import unicodedata  # ← mover aquí, al inicio
from typing import Dict, Any, Optional
import logging

from app.domain.interfaces import ZoneTransformerInterface
from app.domain.transformation_rules import TransformationRulesEngine

logger = logging.getLogger(__name__)


class ZoneTransformer(ZoneTransformerInterface):

    def __init__(self, rules_engine: TransformationRulesEngine = None):
        self.rules_engine = rules_engine or TransformationRulesEngine()

    def normalize_name(self, name: str) -> str:
        """Normaliza el nombre de una zona."""
        if not name or not isinstance(name, str):
            return ""
        name = name.upper()
        name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')
        name = ' '.join(name.split())
        return name

    def _get_negocios_value(self, row: Any) -> float:
        """
        Extrae y valida el valor de negocios (por defecto 0).
        """
        negocios_raw = row.get("negocios")
        if negocios_raw is None or pd.isna(negocios_raw) or str(negocios_raw).strip() == "":
            return 0
        try:
            return float(negocios_raw)
        except (ValueError, TypeError):
            return 0

    def transform_row(self, row: Any) -> Optional[Dict]:
        """
        Transforma una fila del CSV en el formato requerido.
        """
        zone_name_raw = row["zona"]
        zone_name_normalized = self.normalize_name(zone_name_raw)

        # Convertir educación
        educacion_raw = row.get("educacion")
        educacion_years = self.rules_engine.convert_education_to_years(educacion_raw)

        if educacion_years is None:
            logger.warning(f"Educación no válida en fila, omitiendo: {row.to_dict()}")
            return None

        negocios = self._get_negocios_value(row)

        return {
            "zone_code": str(row.get("codigo", row.get("zona_id", row.name))),
            "zone_name": zone_name_normalized,
            "population_density": float(row["poblacion"]),
            "average_income": float(row["ingreso"]),
            "education_level": educacion_years,
            "economic_activity_index": float(row.get("actividad_economica", 0.5)),
            "commercial_presence_index": float(row.get("presencia_comercial", 0.5)),
            "other_variables_json": {
                "raw_poblacion": row["poblacion"],
                "raw_ingreso": row["ingreso"],
                "raw_educacion": educacion_raw,
                "raw_zone_name": zone_name_raw,
                "negocios": negocios
            }
        }