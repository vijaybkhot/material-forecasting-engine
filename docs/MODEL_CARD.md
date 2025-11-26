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

## Model Competition & Selection

To ensure the highest accuracy, we implemented a "Model Showdown" framework where multiple algorithms compete for each material series:

1.  **The Contenders:**

    - **SARIMAX (Seasonal AutoRegressive Integrated Moving Average with eXogenous regressors):** A statistical model excellent for capturing seasonality and the impact of external economic factors (like Interest Rates).
    - **Prophet (by Meta):** A robust additive model that handles missing data and outliers well.
    - **Exponential Smoothing (Holt-Winters):** A classic method focusing on trends and seasonality.
    - **XGBoost / Random Forest:** Tree-based ensemble methods (used as baselines).

2.  **The Winner: SARIMAX**
    - For most construction material indices (Lumber, Steel, Concrete), **SARIMAX** emerged as the clear winner.
    - **Why?** SARIMAX (Seasonal ARIMA) excelled at capturing the complex autocorrelation and monthly seasonality inherent in construction material prices.
    - **Note on Exogenous Variables:** We extensively tested adding external regressors (Housing Starts, Federal Funds Rate, CPI) to both Prophet and SARIMAX models. However, these multivariate models consistently **underperformed** the univariate versions (higher RMSE). This indicates that the historical price history itself contains the strongest predictive signal for short-to-medium term forecasting, and adding external variables introduced more noise than signal.
    - Unlike Prophet, which assumes a decomposable trend+seasonality structure, SARIMAX's autoregressive terms allowed it to better adapt to the recent "cooling" trends in the post-pandemic market.

## Limitations

- Forecasts are based on historical trends and seasonality.
- Does not account for "Black Swan" events (e.g., pandemics, sudden trade wars) unless reflected in the training data.
