from pydantic import BaseModel
from typing import List

class ForecastItem(BaseModel):
    date: str
    forecast: float

class ForecastResponse(BaseModel):
    material_id: str
    forecast: List[ForecastItem]
    source: str
    storage_mode: str