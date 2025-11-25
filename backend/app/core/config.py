import os
from pathlib import Path
from dotenv import load_dotenv

def find_project_root(markers=(".env", "pyproject.toml", ".git")):
    """Traverse upwards to find the project root directory (used for local dev)."""
    start = Path.cwd().resolve()
    for parent in [start, *start.parents]:
        if any((parent / m).exists() for m in markers):
            return parent
    return None

# Allow explicit override (useful for CI / containers)
env_proj = os.getenv("PROJECT_ROOT")
if env_proj:
    PROJECT_ROOT = Path(env_proj)
else:
    # Try to auto-detect (local dev). If detection fails, fall back to the container layout /app.
    detected = find_project_root()
    PROJECT_ROOT = detected if detected is not None else Path("/app")

# Load .env from project root (if present)
dotenv_path = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=dotenv_path)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set in .env file.")

# MODEL_PATH = PROJECT_ROOT / "ml/models/champion_forecasting_model.pkl"
# MANIFEST_PATH = PROJECT_ROOT / "ml/models/champion_forecasting_model_manifest.json"

# Dynamic paths based on material ID
def get_model_paths(material_id: str):
    """Returns tuple: (model_path, manifest_path)"""
    base_dir = PROJECT_ROOT / "ml" / "models"
    return (
        base_dir / f"{material_id}_model.pkl",
        base_dir / f"{material_id}_manifest.json"
    )