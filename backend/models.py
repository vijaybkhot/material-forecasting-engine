from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class RawSeries(Base):
    __tablename__ = 'raw_series'

    id = Column(Integer, primary_key=True, index=True)
    series_id = Column(String, index=True, nullable=False)
    date = Column(DateTime, nullable=False)
    value = Column(Float, nullable=False)
    source = Column(String, default='FRED')

class ModelRegistry(Base):
    __tablename__ = 'models'
    __table_args__ = (UniqueConstraint('name', 'version', name='unique_model_version'),)

    id = Column(Integer, primary_key=True, index=True)

    # Example: "PPI_STEEL_SARIMAX"
    name = Column(String, index=True, nullable=False)
    
    # Example: "v1.0.2" or just a timestamp string if you prefer simple versioning
    version = Column(String, nullable=False)
    
    # The Git Commit Hash that produced this model. Crucial for debugging.
    git_sha = Column(String, nullable=True)
    
    # Training Metadata
    train_start_date = Column(DateTime, nullable=True)
    train_end_date = Column(DateTime, nullable=True)
    
    # Performance Metrics
    primary_metric = Column(String, default="sMAPE")
    # Stores flexible data like {"smape": 9.08, "mae": 12.5}
    metrics_json = Column(JSON, nullable=True)
    
    # Deployment Status
    # Only one model per 'name' should be True at a time
    is_production = Column(Boolean, default=False)
    
    # Audit trail
    created_at = Column(DateTime(timezone=True), server_default=func.now())