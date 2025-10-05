from fastapi import FastAPI

app = FastAPI(title="Contech Forecasting API")

@app.get("/health", tags=["Health"])
def health_check():
    """Checks if the API is running."""
    return {"status": "ok"}