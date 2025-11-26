# Model Card: Material Forecasting Engine

## Model Details
- **Developed by:** Vijay Khot
- **Model Type:** Time-Series Forecasting (SARIMAX, Exponential Smoothing, Prophet)
- **Language:** Python 3.11
- **License:** MIT

## Intended Use
- **Primary Use Case:** Forecasting US Producer Price Indices (PPI) for construction materials (Lumber, Steel, Concrete) and economic indicators (CPI, Housing Starts).
- **Intended Users:** Construction project managers, estimators, and risk analysts.

## Data Sources
- **Federal Reserve Economic Data (FRED):**
  - PPI: Lumber & Wood Products
  - PPI: Iron & Steel
  - PPI: Cement & Concrete
  - CPI: All Items
  - Federal Funds Rate
  - Housing Starts

## Performance
- Models are evaluated using RMSE (Root Mean Squared Error) and MAE (Mean Absolute Error) on a hold-out validation set (last 12-24 months).
- The "Champion" model for each series is selected automatically based on the lowest RMSE.

## Limitations
- Forecasts are based on historical trends and seasonality.
- Does not account for "Black Swan" events (e.g., pandemics, sudden trade wars) unless reflected in the training data.
