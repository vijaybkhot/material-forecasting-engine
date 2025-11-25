import os
import joblib
import redis
import json
import traceback
from fastapi import APIRouter, HTTPException
from app.schemas.forecasting import ForecastResponse
from app.services.forecasting import generate_forecast
from app.database import get_available_materials
from app.database.crud_forecast import get_historical_data
from app.core.config import get_model_paths

# --- Router and Redis Connection ---
router = APIRouter()
redis_url = os.getenv("REDISCLOUD_URL") or os.getenv("REDIS_URL")
redis_client = None

if redis_url:
    try:
        redis_client = redis.from_url(redis_url, decode_responses=True)
        redis_client.ping()
        print("✅ Successfully connected to Redis.")
    except redis.exceptions.ConnectionError as e:
        print(f"⚠️ Could not connect to Redis: {e}. Caching will be disabled.")
        redis_client = None
else:
    print("⚠️ REDIS_URL not set. Caching will be disabled.")

# try:
#     redis_client = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)
#     redis_client.ping()
#     print("✅ Redis connection successful in API.")
# except redis.exceptions.ConnectionError:
#     print("⚠️ Could not connect to Redis. Caching will be disabled.")
#     redis_client = None

# --- API Endpoints ---
@router.get("/materials", tags=["Forecasting"], response_model=list[str])
def get_materials_endpoint():
    materials = get_available_materials()
    if not materials:
        raise HTTPException(status_code=500, detail="Could not retrieve materials from database.")
    return materials

@router.get("/historical-data/{material_id}", tags=["Forecasting"])
def get_historical_data_endpoint(material_id: str):
    """Endpoint to fetch historical data for a given material."""
    data = get_historical_data(series_id=material_id)
    if not data:
        raise HTTPException(status_code=404, detail=f"No historical data found for {material_id}")
    return data


@router.get("/forecast", tags=["Forecasting"], response_model=ForecastResponse)
def get_forecast_endpoint(material_id: str, horizon: int = 12):
    
    # 1. REMOVE the hardcoded check for PPI_STEEL
    # (Delete the 'if material_id != ...' block)

    # 2. Redis Caching (Keep existing logic)
    cache_key = f"forecast:{material_id}:{horizon}"
    # ... (Check redis code) ...

    print(f"⚙️ Generating forecast for '{material_id}'...")
    
    try:
        # 3. Get Dynamic Paths
        model_path, manifest_path = get_model_paths(material_id)
        
        # 4. Check if Model Exists
        if not model_path.exists() or not manifest_path.exists():
            raise HTTPException(
                status_code=404, 
                detail=f"Model for {material_id} not found. Please contact admin to retrain models."
            )

        # 5. Load Model & Manifest
        model = joblib.load(model_path)
        
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
            last_date = manifest.get("last_training_date")

        # 6. Generate Forecast
        # Pass the model AND the date to the service
        forecast_data = generate_forecast(model, last_date, horizon)

        # 7. Cache & Return
        if redis_client:
            redis_client.set(cache_key, json.dumps(forecast_data), ex=3600)

        return ForecastResponse(
            material_id=material_id,
            forecast=forecast_data,
            source="model"
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Model prediction error: {str(e)}")