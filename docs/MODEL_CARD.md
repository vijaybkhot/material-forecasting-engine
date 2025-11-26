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

## The Model Showdown: A Search for the Best Predictor

Our journey to find the most accurate forecasting model unfolded in four distinct stages, with each phase challenging the previous leader.

### Round 1: Setting the Baseline

We began by establishing a performance floor using simple heuristics (**Naive**, **Seasonal Naive**, and **Moving Average**).

- **Result:** These models failed to adapt to recent market volatility, confirming that advanced modeling was necessary.

### Round 2: The Classical Contender (Exponential Smoothing)

We introduced **Holt-Winters Exponential Smoothing**, a classic statistical method.

- **Performance:** It immediately outperformed the baselines by capturing the strong seasonal patterns in construction materials.
- **Status:** It became the "Champion to Beat."

### Round 3: The Modern Challenger (Prophet)

We then tested **Meta's Prophet**, hoping its flexibility with outliers would handle post-pandemic price spikes better.

- **Surprise:** Prophet struggled to match the accuracy of Exponential Smoothing on this specific dataset, often over-smoothing the recent cooling trends.

### Round 4: The Hypothesis Test (External Regressors)

We hypothesized that adding economic indicators (Housing Starts, Interest Rates, CPI) would improve accuracy.

- **The Experiment:** We trained multivariate versions of Prophet and tested the impact of exogenous variables.
- **The Finding:** Surprisingly, these models **underperformed** their univariate counterparts. The external variables introduced more noise than signal for short-term forecasting, proving that the price history itself held the strongest predictive power.

### Round 5: Enter SARIMAX (The Winner)

In the final phase, we introduced **SARIMAX** (Seasonal ARIMA) as a pure, univariate model.

- **The Strategy:** We stripped away the external noise and focused purely on the complex autocorrelation structures within the price history itself.
- **Why it Won:** Unlike Prophet's rigid trend assumptions, SARIMAX's autoregressive terms allowed it to rapidly adapt to the recent market cooling. It captured the complex seasonality that Exponential Smoothing found, but with better error minimization.
- **Outcome:** SARIMAX achieved the lowest RMSE across Lumber, Steel, and Concrete, earning its place as our production model.

## Limitations

- Forecasts are based on historical trends and seasonality.
- Does not account for "Black Swan" events (e.g., pandemics, sudden trade wars) unless reflected in the training data.
