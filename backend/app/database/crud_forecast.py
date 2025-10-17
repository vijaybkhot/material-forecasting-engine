from sqlalchemy import text
from .session import engine 
def get_available_materials():
    """Returns a list of all available forecastable materials from the DB."""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT DISTINCT series_id FROM raw_series"))
            return [row[0] for row in result]
    except Exception as e:
        print(f"Database query failed: {e}")
        return []