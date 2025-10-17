import joblib
import json
import pandas as pd
from app.core.config import MODEL_PATH, MANIFEST_PATH

# Load model and manifest once when the service starts
try:
    model = joblib.load(MODEL_PATH)
    with open(MANIFEST_PATH, 'r') as f:
        model_manifest = json.load(f)
    last_training_date = pd.to_datetime(model_manifest.get("training_data_end_date"))
    print("✅ Model and manifest loaded successfully in service.")
except Exception as e:
    print(f"❌ Failed to load model or manifest in service: {e}")
    model = None
    last_training_date = None

def generate_forecast(horizon: int):
    """Generates a forecast using the loaded champion model."""
    if model is None or last_training_date is None:
        raise RuntimeError("Model or training date is not available.")

    # Generate future dates
    future_dates = pd.date_range(
        start=last_training_date + pd.offsets.MonthBegin(1),
        periods=horizon,
        freq='MS'
    )
    
    # Get forecast values
    forecast_values = model.forecast(steps=horizon)

    # Format the data
    return [
        {"date": d.strftime("%Y-%m-%d"), "forecast": float(v)}
        for d, v in zip(future_dates, forecast_values)
    ]