from fastapi import FastAPI
from app.api.endpoints import forecast
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="Contech Forecasting API", version="1.0")

# --- CORS (Cross-Origin Resource Sharing) Configuration ---
origins = [
    "http://localhost:3000",
    "https://forecasting.vijaykhot.com"
]

origin_regex = r"https://material-forecasting-engine.*\.vercel\.app"

# Add the CORSMiddleware to the application
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow origins listed above
    allow_origin_regex=origin_regex, # Allow origins matching the regex
    allow_credentials=True, # Allow cookies to be included in requests
    allow_methods=["*"],    # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],    # Allow all headers
)

# Include the forecasting router
app.include_router(forecast.router)

# Define a top-level health check endpoint
@app.get("/health", tags=["Health"])
def health_check():
    """Checks if the API is running."""
    return {"status": "ok"}