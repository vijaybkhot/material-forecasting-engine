import os
from pathlib import Path
from dotenv import load_dotenv

def find_project_root(markers=(".env", "pyproject.toml", ".git")):
    """Traverse upwards to find the project root directory."""
    start = Path.cwd().resolve()
    for parent in [start, *start.parents]:
        if any((parent / m).exists() for m in markers):
            return parent
    raise RuntimeError("Project root with one of the markers not found.")

# --- Paths and Settings ---
PROJECT_ROOT = find_project_root()
dotenv_path = PROJECT_ROOT / '.env'
load_dotenv(dotenv_path=dotenv_path)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set in .env file.")

MODEL_PATH = PROJECT_ROOT / "ml/models/champion_forecasting_model.pkl"
MANIFEST_PATH = PROJECT_ROOT / "ml/models/champion_forecasting_model_manifest.json"