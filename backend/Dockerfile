FROM python:3.11-slim
WORKDIR /app

# The context is the ROOT folder (.), so we must provide the full path
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app folder from the backend/ subfolder
COPY backend/app /app/app

# Copy the ml folder from the root
COPY ml /app/ml

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]