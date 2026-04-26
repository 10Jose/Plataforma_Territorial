from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, ForeignKey, Index
from sqlalchemy.sql import func
from app.infrastructure.database import Base


class ScalingExecution(Base):
    __tablename__ = "scaling_executions"

    id = Column(Integer, primary_key=True, index=True)
    transformation_run_id = Column(Integer, nullable=True)
    method = Column(String, nullable=False)
    status = Column(String, default="pending")
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index('ix_scaling_executions_transformation_run_id', 'transformation_run_id'),
    )


class ScaledZoneData(Base):
    """Datos reescalados por zona."""
    __tablename__ = "scaled_zone_data"

    id = Column(Integer, primary_key=True, index=True)
    scaling_execution_id = Column(Integer, ForeignKey("scaling_executions.id"), nullable=False)
    zone_code = Column(String, nullable=False)
    zone_name = Column(String, nullable=False)

    # Variables reescaladas (0-1)
    population_scaled = Column(Float, nullable=False)
    income_scaled = Column(Float, nullable=False)
    education_scaled = Column(Float, nullable=False)
    competition_scaled = Column(Float, nullable=False)

    # Variables originales (trazabilidad)
    population_raw = Column(Float, nullable=True)
    income_raw = Column(Float, nullable=True)
    education_raw = Column(Float, nullable=True)
    competition_raw = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('ix_scaled_zone_data_zone_code', 'zone_code'),
        Index('ix_scaled_zone_data_scaling_execution_id', 'scaling_execution_id'),
    )


class IndicatorResult(Base):
    __tablename__ = "indicator_results"

    id = Column(Integer, primary_key=True, index=True)
    zone_code = Column(String, nullable=False)
    zone_name = Column(String, nullable=False)
    transformation_run_id = Column(Integer, nullable=False)
    population_indicator = Column(Float, nullable=True)
    income_indicator = Column(Float, nullable=True)
    education_indicator = Column(Float, nullable=True)
    competition_indicator = Column(Float, nullable=True)
    composite_indicator_json = Column(JSON, nullable=True)
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('ix_indicator_results_zone_code', 'zone_code'),
        Index('ix_indicator_results_transformation_run_id', 'transformation_run_id'),
    )

class ScoreExecution(Base):
    __tablename__ = "score_executions"

    id = Column(Integer, primary_key=True, index=True)
    scaling_execution_id = Column(Integer, nullable=True)
    business_profile_id = Column(Integer, nullable=True)
    formula_version = Column(String, default="1.0.0")
    weights_json = Column(JSON, nullable=True)
    status = Column(String, default="pending")
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index('ix_score_executions_scaling_execution_id', 'scaling_execution_id'),
    )


class ZoneScore(Base):
    __tablename__ = "zone_scores"

    id = Column(Integer, primary_key=True, index=True)
    score_execution_id = Column(Integer, ForeignKey("score_executions.id"), nullable=False)
    zone_code = Column(String, nullable=False)
    zone_name = Column(String, nullable=False)

    # Score calculado (0-100)
    score_value = Column(Float, nullable=False)

    population_contribution = Column(Float, nullable=True)
    income_contribution = Column(Float, nullable=True)
    education_contribution = Column(Float, nullable=True)
    competition_penalty = Column(Float, nullable=True)

    # Nivel de oportunidad
    opportunity_level = Column(String, nullable=True)  # Alta, Media, Baja

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('ix_zone_scores_zone_code', 'zone_code'),
        Index('ix_zone_scores_score_execution_id', 'score_execution_id'),
    )