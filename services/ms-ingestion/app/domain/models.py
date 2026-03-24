from sqlalchemy import Column, Integer, String, DateTime, JSON, func
from app.infrastructure.database import Base

class DatasetLoad(Base):
    __tablename__ = "dataset_loads"
    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, nullable=False)
    source_name = Column(String)
    source_type = Column(String, nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    uploaded_by = Column(String, nullable=True)
    status = Column(String, default="pending")
    record_count = Column(Integer)
    valid_record_count = Column(Integer, nullable=True)
    invalid_record_count = Column(Integer, nullable=True)
    metadata_json = Column(JSON, nullable=True)