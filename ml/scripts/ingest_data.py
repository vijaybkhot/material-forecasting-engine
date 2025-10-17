import os
import requests
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from pathlib import Path

# --- CONFIGURATION ---
project_root = Path(__file__).resolve().parents[2]
dotenv_path = project_root / '.env'
load_dotenv(dotenv_path=dotenv_path)

DATABASE_URL = os.getenv("DATABASE_URL_ALEMBIC")
FRED_API_KEY = os.getenv("FRED_API_KEY")

SERIES_TO_FETCH = {
    'WPU101702': 'PPI_STEEL',
    'WPU102': 'PPI_LUMBER',
    'PCU327320327320': 'PPI_CONCRETE',
    'HOUST': 'HOUSING_STARTS',
    'CPIAUCSL': 'CPI_ALL',
    'FEDFUNDS': 'FED_FUNDS_RATE'
}

# --- FUNCTIONS ---

def fetch_series_data(series_id, api_key):
    """Fetches a single time series from the FRED API."""
    print(f"Fetching data for series: {series_id}...")
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={api_key}&file_type=json"
    response = requests.get(url)
    response.raise_for_status()
    
    data = response.json()
    observations = data.get('observations', [])
    
    if not observations:
        print(f"Warning: No observations found for series {series_id}.")
        return pd.DataFrame()

    df = pd.DataFrame(observations)
    df = df[['date', 'value']]
    df['date'] = pd.to_datetime(df['date'])
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    df.dropna(inplace=True)
    return df

def save_to_db(df, table_name, engine):
    """Creates the table if needed and saves the DataFrame, all in one transaction."""
    with engine.connect() as connection:
        # This 'begin()' block automatically handles the transaction.
        with connection.begin() as transaction:
            # 1. Ensure the table exists (moved logic here)
            print(f"Ensuring table '{table_name}' exists...")
            connection.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    date DATE NOT NULL,
                    value DOUBLE PRECISION,
                    series_id TEXT NOT NULL,
                    source TEXT,
                    PRIMARY KEY (series_id, date)
                );
            """))

            # 2. Delete old data for the series being ingested
            for series_id in df['series_id'].unique():
                print(f"Deleting old data for {series_id}...")
                connection.execute(text(f"DELETE FROM {table_name} WHERE series_id = :series_id"), {'series_id': series_id})

            # 3. Insert the new data
            print("Inserting new data...")
            df.to_sql(table_name, connection, if_exists='append', index=False)
            
    print("Data insertion complete and transaction committed.")

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    print("Starting data ingestion process...")
    
    engine = create_engine(DATABASE_URL)
    all_series_df = pd.DataFrame()

    for fred_code, our_id in SERIES_TO_FETCH.items():
        try:
            series_df = fetch_series_data(fred_code, FRED_API_KEY)
            if not series_df.empty:
                series_df['series_id'] = our_id
                series_df['source'] = 'FRED'
                all_series_df = pd.concat([all_series_df, series_df], ignore_index=True)
        except requests.HTTPError as e:
            print(f"Error fetching data for {fred_code}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred for {fred_code}: {e}")

    if not all_series_df.empty:
        # The save_to_db function now handles table creation
        save_to_db(all_series_df, 'raw_series', engine)
    else:
        print("No data was fetched. Database not updated.")
        
    print("Data ingestion process finished.")