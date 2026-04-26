from sqlalchemy import Column, Integer, String, DateTime, JSON, Index
from sqlalchemy.sql import func
from app.infrastructure.database import Base


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, index=True)
    trace_id = Column(String, nullable=False, index=True)
    service_name = Column(String, nullable=False, index=True)
    event_type = Column(String, nullable=False, index=True)
    reference_id = Column(String, nullable=True)
    user_id = Column(Integer, nullable=True)
    username = Column(String, nullable=True)
    details_json = Column(JSON, nullable=True)
    status = Column(String, default="success")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
