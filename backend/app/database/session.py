from sqlalchemy import create_engine
from app.core.config import DATABASE_URL

# SQLAlchemy expects the 'postgresql' dialect name. Some platforms
# (Heroku) provide DATABASE_URL with the old 'postgres://' scheme.
# Normalize that to 'postgresql://' so SQLAlchemy can load the correct
# dialect plugin and avoid NoSuchModuleError: Can't load plugin: sqlalchemy.dialects:postgres
db_url = DATABASE_URL.replace("postgres://", "postgresql://", 1) if DATABASE_URL else DATABASE_URL

# Create a single, reusable engine that manages a connection pool
engine = create_engine(db_url)