from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, JSON, Index
from sqlalchemy.sql import func
from app.infrastructure.database import Base


class MLExperiment(Base):
    __tablename__ = "ml_experiments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    problem_type = Column(String, default="regression")
    target_variable = Column(String, nullable=False)
    algorithm = Column(String, nullable=False)
    features_used = Column(JSON, nullable=True)
    evaluation_metric = Column(String, nullable=True)
    metric_value = Column(Float, nullable=True)
    executed_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default="pending")

    __table_args__ = (
        Index('ix_ml_experiments_status', 'status'),
    )


class TrainedModel(Base):
    __tablename__ = "trained_models"

    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(Integer, nullable=False)
    model_name = Column(String, nullable=False)
    model_version = Column(String, nullable=False)
    storage_path = Column(String, nullable=True)
    trained_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default="active")
    is_active = Column(Boolean, default=False)

    __table_args__ = (
        Index('ix_trained_models_is_active', 'is_active'),
    )


class PredictionResult(Base):
    __tablename__ = "prediction_results"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, nullable=False)
    zone_code = Column(String, nullable=False)
    zone_name = Column(String, nullable=False)
    prediction_value = Column(Float, nullable=False)
    prediction_label = Column(String, nullable=True)
    confidence_score = Column(Float, nullable=True)
    predicted_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('ix_prediction_results_zone_code', 'zone_code'),
    )