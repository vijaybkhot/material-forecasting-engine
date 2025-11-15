# filepath: backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# NOTE: Build context MUST be repo root so paths like backend/requirements.txt resolve.
# Install dependencies first (cache layer)
COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r /tmp/requirements.txt

# Copy backend code and models
COPY backend/app /app/app
COPY ml /app/ml

# Reduce image size by clearing pip cache (already using --no-cache-dir) & verify model manifest exists
RUN test -f /app/ml/models/champion_forecasting_model_manifest.json || echo "[WARN] Model manifest missing; ensure ml/models is populated before deploy." && ls -1 /app/ml/models || true

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
