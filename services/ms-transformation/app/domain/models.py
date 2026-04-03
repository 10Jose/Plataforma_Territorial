from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Float, Index
from sqlalchemy.sql import func
from app.infrastructure.database import Base

class TransformationRun(Base):
    __tablename__ = "transformation_runs"

    id = Column(Integer, primary_key=True, index=True)
    dataset_load_id = Column(Integer, nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, default="pending")
    rules_applied = Column(JSON, nullable=True)
    output_version = Column(String, nullable=True)


class TransformedZoneData(Base):
    __tablename__ = "transformed_zone_data"

    id = Column(Integer, primary_key=True, index=True)
    transformation_run_id = Column(Integer, ForeignKey("transformation_runs.id"), nullable=False)
    zone_code = Column(String, nullable=False)
    zone_name = Column(String, nullable=False)
    population_density = Column(Integer, nullable=False)
    average_income = Column(Integer, nullable=False)
    education_level = Column(Integer, nullable=False)
    economic_activity_index = Column(Float, nullable=True)
    commercial_presence_index = Column(Float, nullable=True)
    other_variables_json = Column(JSON, nullable=True)


    __table_args__ = (
        Index('ix_transformed_zone_data_zone_name', 'zone_name'),
        Index('ix_transformed_zone_data_zone_code', 'zone_code'),
    )