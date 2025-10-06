import os
import requests
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# --- CONFIGURATION ---
# Load environment variables from the .env file in the project root
from pathlib import Path

# Build an absolute path to the .env file in the project root
# This is robust and works no matter where you run the script from
project_root = Path(__file__).resolve().parents[2]
dotenv_path = project_root / '.env'
load_dotenv(dotenv_path=dotenv_path)


# Get the database URL and FRED API key from environment variables
DATABASE_URL = os.getenv("DATABASE_URL_ALEMBIC") # Using the alembic URL for localhost connection
FRED_API_KEY = os.getenv("FRED_API_KEY")

# Define the economic series we want to fetch from FRED
# Format is 'FRED_SERIES_CODE': 'our_series_id'
SERIES_TO_FETCH = {
    'WPU101702': 'PPI_STEEL', # Steel Mill Products
    'WPU102': 'PPI_LUMBER', # Lumber and Wood Products
    'PCU327320327320': 'PPI_CONCRETE', # Ready-Mix Concrete
    'HOUST': 'HOUSING_STARTS', # Housing Starts
    'CPIAUCSL': 'CPI_ALL', # Consumer Price Index
    'FEDFUNDS': 'FED_FUNDS_RATE' # Federal Funds Rate
}

# --- FUNCTIONS ---

def fetch_series_data(series_id, api_key):
    """Fetches a single time series from the FRED API."""
    print(f"Fetching data for series: {series_id}...")
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={api_key}&file_type=json"
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for bad status codes
    
    data = response.json()
    observations = data.get('observations', [])
    
    if not observations:
        print(f"Warning: No observations found for series {series_id}.")
        return pd.DataFrame()

    df = pd.DataFrame(observations)
    df = df[['date', 'value']]
    df['date'] = pd.to_datetime(df['date'])
    # FRED uses '.' to represent missing data, convert to numeric and handle errors
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    df.dropna(inplace=True) # Drop rows where value could not be converted
    return df

def save_to_db(df, table_name, engine):
    """Saves a DataFrame to the database, ensuring idempotency."""
    with engine.connect() as connection:
        # This 'begin()' block automatically handles the transaction.
        # It will COMMIT on success or ROLLBACK on an error.
        with connection.begin() as transaction:
            for series_id in df['series_id'].unique():
                print(f"Deleting old data for {series_id}...")
                connection.execute(text(f"DELETE FROM {table_name} WHERE series_id = :series_id"), {'series_id': series_id})

            print("Inserting new data...")
            df.to_sql(table_name, connection, if_exists='append', index=False)

    print("Data insertion complete and transaction committed.")

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    print("Starting data ingestion process...")
    
    # Create a SQLAlchemy engine to connect to the database
    engine = create_engine(DATABASE_URL)
    
    all_series_df = pd.DataFrame()

    # Loop through each series, fetch the data, and append it to one big DataFrame
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

    # Save the combined DataFrame to the database
    if not all_series_df.empty:
        save_to_db(all_series_df, 'raw_series', engine)
    else:
        print("No data was fetched. Database not updated.")
        
    print("Data ingestion process finished.")