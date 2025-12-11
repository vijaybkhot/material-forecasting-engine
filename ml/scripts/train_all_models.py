import os
import sys
import json
import pandas as pd
import joblib
from sqlalchemy import create_engine, text
from statsmodels.tsa.statespace.sarimax import SARIMAX
from pathlib import Path
from dotenv import load_dotenv

# --- SETUP PATHS ---
PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODELS_DIR = PROJECT_ROOT / "ml" / "models"
LOGS_DIR = PROJECT_ROOT / "logs"

# Detect environment: Docker or Local
is_docker = os.path.exists('/.dockerenv')

if is_docker:
    # In Docker: /app is root, app module is at /app/app
    sys.path.insert(0, '/app')
else:
    # Local: need to add backend directory
    sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.core.artifact_manager import ArtifactManager

# Load Environment Variables
load_dotenv(PROJECT_ROOT / ".env")

# Get Database URL
DATABASE_URL = os.getenv("DATABASE_URL_ALEMBIC") or os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set. Cannot fetch data.")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

def train_material(series_id, manager):
    print(f"\n🏭 Processing: {series_id}...")
    
    # Fetch Data
    query = text("SELECT date, value FROM raw_series WHERE series_id = :series_id ORDER BY date")
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params={"series_id": series_id})
    
    if df.empty:
        print(f"   ⚠️  No data found for {series_id}. Skipping.")
        return

    # Preprocess
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    df = df.asfreq('MS').ffill()

    try:
        # Train SARIMAX
        model = SARIMAX(df['value'], 
                        order=(1, 1, 1), 
                        seasonal_order=(1, 1, 1, 12),
                        enforce_stationarity=False,
                        enforce_invertibility=False)
        results = model.fit(disp=False)

        # Save Artifacts
        manifest = {
            "series_id": series_id,
            "last_training_date": str(df.index[-1]),
            "model_type": "SARIMAX (1,1,1)(1,1,1,12)"
        }
        
        manager.save_model(series_id, results, manifest)

        print(f"   ✅ Successfully saved model and manifest for {series_id}")

    except Exception as e:
        print(f"   ❌ Error training {series_id}: {e}")

def main():
    os.makedirs(MODELS_DIR, exist_ok=True)

    try:
        manager = ArtifactManager()
        print(f"📦 Artifact Storage Mode: {manager.mode}")
    except Exception as e:
        print(f"❌ Failed to initialize ArtifactManager: {e}")
        return

    with engine.connect() as conn:
        result = conn.execute(text("SELECT DISTINCT series_id FROM raw_series"))
        materials = [row[0] for row in result]

    print(f"Found {len(materials)} materials in database: {materials}")

    for material in materials:
        train_material(material, manager)

if __name__ == "__main__":
    main()