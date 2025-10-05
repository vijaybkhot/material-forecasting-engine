from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class RawSeries(Base):
    __tablename__ = 'raw_series'

    id = Column(Integer, primary_key=True, index=True)
    series_id = Column(String, index=True, nullable=False)
    date = Column(DateTime, nullable=False)
    value = Column(Float, nullable=False)
    source = Column(String, default='FRED')