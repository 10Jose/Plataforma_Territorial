from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func
from app.domain.models import ScalingExecution
from app.domain.interfaces import IScalingExecutionService


class ScalingExecutionService(IScalingExecutionService):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_execution(self, method: str) -> int:
        """retorna su ID."""
        execution = ScalingExecution(
            method=method,
            status="processing"
        )
        self.db.add(execution)
        await self.db.flush()
        return execution.id

    async def mark_completed(self, execution_id: int) -> None:
        """Marca una ejecución como completada."""
        execution = await self.db.get(ScalingExecution, execution_id)
        if execution:
            execution.status = "completed"
            execution.finished_at = func.now()
            await self.db.commit()
            await self.db.refresh(execution)

    async def mark_failed(self, execution_id: int) -> None:
        """Marca una ejecución como fallida."""
        execution = await self.db.get(ScalingExecution, execution_id)
        if execution:
            execution.status = "failed"
            await self.db.commit()
