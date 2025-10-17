import redis
import json
import traceback
from fastapi import APIRouter, HTTPException
from app.schemas.forecasting import ForecastResponse
from app.services.forecasting import generate_forecast
from app.database import get_available_materials

# --- Router and Redis Connection ---
router = APIRouter()

try:
    redis_client = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)
    redis_client.ping()
    print("✅ Redis connection successful in API.")
except redis.exceptions.ConnectionError:
    print("⚠️ Could not connect to Redis. Caching will be disabled.")
    redis_client = None

# --- API Endpoints ---
@router.get("/materials", tags=["Forecasting"], response_model=list[str])
def get_materials_endpoint():
    materials = get_available_materials()
    if not materials:
        raise HTTPException(status_code=500, detail="Could not retrieve materials from database.")
    return materials

@router.get("/forecast", tags=["Forecasting"], response_model=ForecastResponse)
def get_forecast_endpoint(material_id: str, horizon: int = 12):
    if material_id != 'PPI_STEEL':
        raise HTTPException(status_code=400, detail="Forecasting is currently only supported for 'PPI_STEEL'.")

    # Caching Logic
    cache_key = f"forecast:{material_id}:{horizon}"
    if redis_client:
        cached_result = redis_client.get(cache_key)
        if cached_result:
            print(f"✔️ Serving forecast for '{material_id}' from cache.")
            return ForecastResponse(material_id=material_id, forecast=json.loads(cached_result), source="cache")

    print(f"⚙️ Generating new forecast for '{material_id}' using the model.")
    try:
        forecast_data = generate_forecast(horizon=horizon)
        if redis_client:
            redis_client.set(cache_key, json.dumps(forecast_data), ex=3600)
        return ForecastResponse(material_id=material_id, forecast=forecast_data, source="model")
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Model prediction error: {e}")