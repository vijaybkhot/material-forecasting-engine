import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from statsmodels.tsa.statespace.sarimax import SARIMAX
from pathlib import Path
from dotenv import load_dotenv

# --- SETUP PATHS ---
PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODELS_DIR = PROJECT_ROOT / "ml" / "models"

# Detect environment: Docker or Local
is_docker = os.path.exists('/.dockerenv')

if is_docker:
    # In Docker: /app is root. models.py is at /app/models.py
    sys.path.insert(0, '/app')
else:
    # Local: backend is at PROJECT_ROOT/backend
    sys.path.insert(0, str(PROJECT_ROOT / "backend"))

# --- IMPORTS (Late imports to ensure sys.path is set) ---
try:
    from app.core.artifact_manager import ArtifactManager
    from models import ModelRegistry  # Importing directly from backend/models.py
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print(f"DEBUG: sys.path: {sys.path}")
    sys.exit(1)

# Load Environment Variables
load_dotenv(PROJECT_ROOT / ".env")

# Get Database URL
DATABASE_URL =  os.getenv("DATABASE_URL") or os.getenv("DATABASE_URL_ALEMBIC")
if not DATABASE_URL:
    print("⚠️  DATABASE_URL not set. Using dummy mode (no DB writes).")
    engine = None
else:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- HELPER FUNCTIONS ---

def get_git_sha():
    """
    Robust way to get the current Git Commit SHA.
    1. Checks HEROKU_SLUG_COMMIT (Production)
    2. Checks GIT_SHA (CI/Docker)
    3. Checks gitpython (Local Dev)
    """
    # Heroku Production
    if os.getenv("HEROKU_SLUG_COMMIT"):
        return os.getenv("HEROKU_SLUG_COMMIT")[:7]
    
    # Docker/CI injection
    if os.getenv("GIT_SHA"):
        return os.getenv("GIT_SHA")[:7]
        
    # Local Development
    try:
        import git
        repo = git.Repo(search_parent_directories=True)
        return repo.head.object.hexsha[:7]
    except Exception:
        return "unknown"

def calculate_smape(actual, predicted):
    """
    Calculates Symmetric Mean Absolute Percentage Error (sMAPE).
    Range: 0% to 200% (Lower is better)
    """
    return 100/len(actual) * np.sum(2 * np.abs(predicted - actual) / (np.abs(actual) + np.abs(predicted)))

def train_and_register(series_id, manager):
    print(f"\n🏭 Processing: {series_id}...")
    
    if not engine:
        print("   ⚠️  No DB connection. Skipping.")
        return

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
    df = df.asfreq('MS').ffill()
    
    train_start = df.index[0]
    train_end = df.index[-1]

    try:
        # 3. Train SARIMAX
        # (Note: In a real system, you might grid-search these parameters)
        model = SARIMAX(df['value'], 
                        order=(1, 1, 1), 
                        seasonal_order=(1, 1, 1, 12),
                        enforce_stationarity=False,
                        enforce_invertibility=False)
        results = model.fit(disp=False)

        # 4. Calculate Metrics
        fitted_values = results.fittedvalues
        smape_score = calculate_smape(df['value'], fitted_values)
        metrics = {"sMAPE": round(smape_score, 4)}

        # 5. Prepare Metadata
        version_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        git_sha = get_git_sha()
        
        manifest = {
            "series_id": series_id,
            "version": version_id,
            "git_sha": git_sha,
            "metrics": metrics,
            "last_training_date": str(train_end)
        }
        
        # 6. Save Artifact (S3 or Local)
        manager.save_model(series_id, results, manifest)
        print(f"   ✅ Artifact saved ({manager.mode})")

        # 7. Register in Database
        session = SessionLocal()
        try:
            # Check if this exact version exists (sanity check)
            existing = session.query(ModelRegistry).filter_by(name=series_id, version=version_id).first()
            if not existing:
                new_model = ModelRegistry(
                    name=series_id,
                    version=version_id,
                    git_sha=git_sha,
                    train_start_date=train_start,
                    train_end_date=train_end,
                    primary_metric="sMAPE",
                    metrics_json=metrics,
                    is_production=False  # Default to False
                )
                session.add(new_model)
                session.commit()
                print(f"   📝 Registered in DB: {series_id} v{version_id} (sMAPE: {smape_score:.2f}%)")
            else:
                print(f"   ⚠️  Model version already exists in DB.")
        except Exception as e:
            session.rollback()
            print(f"   ❌ DB Insert Failed: {e}")
        finally:
            session.close()

    except Exception as e:
        print(f"   ❌ Training Failed: {e}")

def main():
    try:
        manager = ArtifactManager()
        print(f"📦 Storage Mode: {manager.mode}")
        print(f"🐙 Git SHA: {get_git_sha()}")
    except Exception as e:
        print(f"❌ Failed to init ArtifactManager: {e}")
        return

    # Get list of materials
    if engine:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT DISTINCT series_id FROM raw_series"))
            materials = [row[0] for row in result]
    else:
        materials = []

    print(f"🎯 Found {len(materials)} materials to train.")

    for material in materials:
        train_and_register(material, manager)

if __name__ == "__main__":
    main()