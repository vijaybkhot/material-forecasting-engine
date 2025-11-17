# This file should be in your PROJECT ROOT.

FROM python:3.11-slim
WORKDIR /app

# The build context is the ROOT (.), so we must use the full path
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code from the backend/app subfolder
COPY backend/app /app/app

# Copy alembic files from the backend/ subfolder
COPY backend/alembic /app/alembic
COPY backend/alembic.ini /app/alembic.ini

# Copy the ml folder from the root
COPY ml /app/ml

EXPOSE 8000
# This CMD is correct for Heroku
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]