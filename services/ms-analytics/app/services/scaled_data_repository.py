from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict
from app.domain.models import ScaledZoneData
from app.domain.interfaces import IScaledDataRepository


class ScaledDataRepository(IScaledDataRepository):
    """Repositorio para datos reescalados."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(self, scaling_execution_id: int, scaled_data: List[Dict]) -> int:
        """Guarda datos reescalados y retorna cantidad guardada."""
        count = 0
        for item in scaled_data:
            record = ScaledZoneData(
                scaling_execution_id=scaling_execution_id,
                zone_code=item["zone_code"],
                zone_name=item["zone_name"],
                population_scaled=item["population_scaled"],
                income_scaled=item["income_scaled"],
                education_scaled=item["education_scaled"],
                competition_scaled=item["competition_scaled"],
                population_raw=item["population_raw"],
                income_raw=item["income_raw"],
                education_raw=item["education_raw"],
                competition_raw=item["competition_raw"]
            )
            self.db.add(record)
            count += 1

        await self.db.commit()
        return count