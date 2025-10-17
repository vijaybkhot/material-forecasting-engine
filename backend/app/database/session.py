from sqlalchemy import create_engine
from app.core.config import DATABASE_URL

# Create a single, reusable engine that manages a connection pool
engine = create_engine(DATABASE_URL)