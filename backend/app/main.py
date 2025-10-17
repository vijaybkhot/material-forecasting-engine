from fastapi import FastAPI
from app.api.endpoints import forecast

app = FastAPI(title="Contech Forecasting API", version="1.0")

# Include the forecasting router
app.include_router(forecast.router)

# Define a top-level health check endpoint
@app.get("/health", tags=["Health"])
def health_check():
    """Checks if the API is running."""
    return {"status": "ok"}