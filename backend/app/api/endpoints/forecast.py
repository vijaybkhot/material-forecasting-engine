import os
import redis
import json
import traceback
from fastapi import APIRouter, HTTPException
from app.schemas.forecasting import ForecastResponse
from app.services.forecasting import generate_forecast
from app.database import get_available_materials
from app.database.crud_forecast import get_historical_data
from app.core.artifact_manager import ArtifactManager

# --- Router and Redis Connection ---
router = APIRouter()
redis_url = os.getenv("REDISCLOUD_URL") or os.getenv("REDIS_URL") or "redis://redis:6379/0"
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
    
    # Initialize Artifact Manager early to track storage source
    artifact_manager = ArtifactManager()
    print(f"📦 Using storage mode: {artifact_manager.mode}")
    
    # 1. Redis Caching Strategy
    cache_key = f"forecast:{material_id}:{horizon}"
    if redis_client:
        try:
            cached_forecast = redis_client.get(cache_key)
            if cached_forecast:
                print(f"⚡ Cache HIT for {material_id}")
                return ForecastResponse(
                    material_id=material_id,
                    forecast=json.loads(cached_forecast),
                    source="cache",
                    storage_mode=artifact_manager.mode
                )
        except Exception as e:
            print(f"⚠️ Redis cache error: {e}")

    print(f"⚙️ Generating forecast for '{material_id}'...")
    
    try:
        # 2. Load Model from storage (LOCAL or S3)
        try:
            print(f"📥 Loading model from {artifact_manager.mode}...")
            model = artifact_manager.load_model(material_id)
            print(f"✅ Model loaded from {artifact_manager.mode}")
        except Exception as e:
            # If the manager fails to find/load the file, we return a 404
            print(f"❌ Model not found for {material_id}: {e}")
            raise HTTPException(
                status_code=404, 
                detail=f"Model for {material_id} not found. Please contact admin to retrain models."
            )

        # 3. Load Manifest (Metadata) from storage (LOCAL or S3)
        # We need this to get the 'last_training_date' for the forecast service
        try:
            print(f"📥 Loading manifest from {artifact_manager.mode}...")
            manifest = artifact_manager.load_manifest(material_id)
            last_date = manifest.get("last_training_date")
            if not last_date:
                raise ValueError("Manifest missing 'last_training_date'")
            print(f"✅ Manifest loaded from {artifact_manager.mode}")
        except Exception as e:
            print(f"❌ Manifest error for {material_id}: {e}")
            raise HTTPException(
                status_code=404, 
                detail=f"Model metadata (manifest) for {material_id} is missing or invalid."
            )

        # 4. Generate Forecast
        print(f"🔮 Generating {horizon}-month forecast...")
        forecast_data = generate_forecast(model, last_date, horizon)
        print(f"✅ Forecast generated successfully from {artifact_manager.mode}")

        # 5. Cache & Return
        if redis_client:
            try:
                redis_client.set(cache_key, json.dumps(forecast_data), ex=3600)
                print(f"💾 Forecast cached in Redis")
            except Exception as e:
                print(f"⚠️ Redis caching failed (forecast still returned): {e}")

        return ForecastResponse(
            material_id=material_id,
            forecast=forecast_data,
            source="model",
            storage_mode=artifact_manager.mode
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Model prediction error: {str(e)}")