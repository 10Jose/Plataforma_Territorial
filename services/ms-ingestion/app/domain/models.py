from sqlalchemy import Column, Integer, String, DateTime, JSON, func, ForeignKey
from app.infrastructure.database import Base

class DatasetLoad(Base):
    __tablename__ = "dataset_loads"
    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, nullable=False)
    source_name = Column(String, nullable=True)
    source_type = Column(String, nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    uploaded_by = Column(String, nullable=True)
    status = Column(String, default="pending", nullable= False)
    validation_status = Column(String, nullable=True)
    schema_version = Column(String, nullable=True)
    record_count = Column(Integer, nullable=True)
    valid_record_count = Column(Integer, nullable=True)
    invalid_record_count = Column(Integer, nullable=True)
    metadata_json = Column(JSON, nullable=True)

class DatasetFileReference(Base):
    __tablename__ = "dataset_file_references"

    id = Column(Integer, primary_key=True, index=True)
    dataset_load_id = Column(Integer, ForeignKey("dataset_loads.id"), nullable=False)
    storage_path = Column(String, nullable=False)      # ruta donde se guardó el archivo
    file_format = Column(String, nullable=False)       # "CSV"
    checksum = Column(String, nullable=True)           # hash del archivo para integridad
    created_at = Column(DateTime(timezone=True), server_default=func.now())