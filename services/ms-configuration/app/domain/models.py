from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Index
from sqlalchemy.sql import func
from app.infrastructure.database import Base


class BusinessProfile(Base):
    __tablename__ = "business_profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    target_business_type = Column(String, nullable=False)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('ix_business_profiles_is_active', 'is_active'),
    )


class ScoringConfiguration(Base):
    __tablename__ = "scoring_configurations"

    id = Column(Integer, primary_key=True, index=True)
    business_profile_id = Column(Integer, nullable=False)
    population_weight = Column(Integer, nullable=False, default=25)
    income_weight = Column(Integer, nullable=False, default=25)
    education_weight = Column(Integer, nullable=False, default=25)
    competition_weight = Column(Integer, nullable=False, default=25)
    additional_weights_json = Column(JSON, nullable=True)
    formula_version = Column(String, default="1.0.0")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

    __table_args__ = (
        Index('ix_scoring_configurations_business_profile_id', 'business_profile_id'),
        Index('ix_scoring_configurations_is_active', 'is_active'),
    )