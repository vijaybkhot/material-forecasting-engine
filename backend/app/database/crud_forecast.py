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

def get_historical_data(series_id: str):
    """Fetches all historical data points for a given series_id."""
    try:
        with engine.connect() as connection:
            query = text("SELECT date, value FROM raw_series WHERE series_id = :series_id ORDER BY date")
            result = connection.execute(query, {"series_id": series_id})
            # Return data in a format easily convertible to JSON
            return [{"date": row.date.strftime('%Y-%m-%d'), "value": row.value} for row in result]
    except Exception as e:
        print(f"Database query for historical data failed: {e}")
        return []