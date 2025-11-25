import os
import json
import pandas as pd
import joblib
from sqlalchemy import create_engine, text
from statsmodels.tsa.statespace.sarimax import SARIMAX
from pathlib import Path
from dotenv import load_dotenv

# --- SETUP PATHS ---
# This ensures it works on your machine
PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODELS_DIR = PROJECT_ROOT / "ml" / "models"
LOGS_DIR = PROJECT_ROOT / "logs"

# Load Environment Variables
load_dotenv(PROJECT_ROOT / ".env")

# Get Database URL (Logic to handle Local vs Heroku formats)
DATABASE_URL = os.getenv("DATABASE_URL_ALEMBIC") or os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set. Cannot fetch data.")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

def train_material(series_id):
    print(f"\n🏭 Processing: {series_id}...")
    
    # 1. Fetch Data
    query = text("SELECT date, value FROM raw_series WHERE series_id = :series_id ORDER BY date")
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params={"series_id": series_id})
    
    if df.empty:
        print(f"   ⚠️  No data found for {series_id}. Skipping.")
        return

    # 2. Preprocess
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    df = df.asfreq('MS').ffill() # Monthly frequency, fill gaps

    # 3. Train SARIMAX
    # We use a robust baseline config: (1,1,1) x (1,1,1,12)
    try:
        model = SARIMAX(df['value'], 
                        order=(1, 1, 1), 
                        seasonal_order=(1, 1, 1, 12),
                        enforce_stationarity=False,
                        enforce_invertibility=False)
        results = model.fit(disp=False)

        # 4. Save Artifacts
        # Save Model (.pkl)
        model_path = MODELS_DIR / f"{series_id}_model.pkl"
        joblib.dump(results, model_path)
        
        # Save Manifest (.json) - Helper for the API to know dates
        manifest = {
            "series_id": series_id,
            "last_training_date": str(df.index[-1]),
            "model_type": "SARIMAX (1,1,1)(1,1,1,12)"
        }
        manifest_path = MODELS_DIR / f"{series_id}_manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest, f)

        print(f"   ✅ Successfully saved model and manifest for {series_id}")

    except Exception as e:
        print(f"   ❌ Error training {series_id}: {e}")

def main():
    # Ensure output directory exists
    os.makedirs(MODELS_DIR, exist_ok=True)

    # Get list of all materials
    with engine.connect() as conn:
        result = conn.execute(text("SELECT DISTINCT series_id FROM raw_series"))
        materials = [row[0] for row in result]

    print(f"Found {len(materials)} materials in database: {materials}")

    for material in materials:
        train_material(material)

if __name__ == "__main__":
    main()