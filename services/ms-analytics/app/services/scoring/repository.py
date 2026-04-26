from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.sql import func
from app.domain.models import ScoreExecution, ZoneScore, ScaledZoneData
from app.domain.interfaces import IScoringRepository


class ScoringRepository(IScoringRepository):
    """Repositorio para scoring (SRP)."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_execution(self, execution_data: Dict) -> int:
        execution = ScoreExecution(
            formula_version=execution_data.get("formula_version", "1.0.0"),
            weights_json=execution_data.get("weights"),
            status="processing"
        )
        self.db.add(execution)
        await self.db.flush()
        return execution.id

    async def save_scores(self, execution_id: int, scores: List[Dict]) -> int:
        count = 0
        for score_data in scores:
            zone_score = ZoneScore(
                score_execution_id=execution_id,
                zone_code=score_data["zone_code"],
                zone_name=score_data["zone_name"],
                score_value=score_data["score_value"],
                population_contribution=score_data["population_contribution"],
                income_contribution=score_data["income_contribution"],
                education_contribution=score_data["education_contribution"],
                competition_penalty=score_data["competition_penalty"],
                opportunity_level=score_data["opportunity_level"]
            )
            self.db.add(zone_score)
            count += 1

        await self.db.commit()
        return count

    async def update_execution_status(self, execution_id: int, status: str) -> None:
        execution = await self.db.get(ScoreExecution, execution_id)
        if execution:
            execution.status = status
            if status == "completed":
                execution.finished_at = func.now()
            await self.db.commit()

    async def get_latest_execution(self) -> Optional[Dict]:
        stmt = select(ScoreExecution).where(
            ScoreExecution.status == "completed"
        ).order_by(ScoreExecution.finished_at.desc()).limit(1)
        result = await self.db.execute(stmt)
        execution = result.scalar_one_or_none()

        if not execution:
            return None

        return {
            "id": execution.id,
            "weights": execution.weights_json,
            "formula_version": execution.formula_version,
            "finished_at": execution.finished_at
        }

    async def get_scores(self, execution_id: int, zone_code: Optional[str] = None) -> List[Dict]:
        stmt = select(ZoneScore).where(
            ZoneScore.score_execution_id == execution_id
        ).order_by(ZoneScore.score_value.desc())

        if zone_code:
            stmt = stmt.where(ZoneScore.zone_code == zone_code)

        result = await self.db.execute(stmt)
        scores = result.scalars().all()

        return [
            {
                "id": s.id,
                "zone_code": s.zone_code,
                "zone_name": s.zone_name,
                "score": s.score_value,
                "opportunity_level": s.opportunity_level,
                "contributions": {
                    "population": s.population_contribution,
                    "income": s.income_contribution,
                    "education": s.education_contribution,
                    "competition_penalty": s.competition_penalty
                },
                "calculated_at": s.created_at
            }
            for s in scores
        ]

    async def get_scaled_data(self) -> List:
        stmt = select(ScaledZoneData).order_by(ScaledZoneData.created_at.desc())
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_scaled_data_by_zone(self, zone_code: str):
        """Obtiene los datos reescalados de una zona específica."""
        stmt = select(ScaledZoneData).where(
            ScaledZoneData.zone_code == zone_code
        ).order_by(ScaledZoneData.created_at.desc()).limit(1)

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def clear_all(self) -> None:
        await self.db.execute(delete(ZoneScore))
        await self.db.execute(delete(ScoreExecution))
        await self.db.commit()