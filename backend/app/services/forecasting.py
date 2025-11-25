import pandas as pd

def generate_forecast(model, last_training_date, horizon: int):
    """
    Generates forecast using a loaded model object passed from the API.
    This function is stateless and works for any material model.
    """
    try:
        # 1. Calculate future dates
        # We use the last_training_date passed from the API (read from the specific material's manifest)
        start_date = pd.to_datetime(last_training_date)
        
        # Generate the range starting from the month AFTER the last training data
        future_dates = pd.date_range(
            start=start_date + pd.DateOffset(months=1), 
            periods=horizon, 
            freq='MS'
        )

        # 2. Generate Predictions
        # The model object is already loaded by the API endpoint and passed here
        forecast_values = model.forecast(steps=horizon)

        # 3. Format Output
        formatted_forecast = []
        for date, value in zip(future_dates, forecast_values):
            formatted_forecast.append({
                "date": date.strftime("%Y-%m-%d"),
                "forecast": round(value, 2)
            })
            
        return formatted_forecast

    except Exception as e:
        print(f"Error in generate_forecast: {e}")
        raise e