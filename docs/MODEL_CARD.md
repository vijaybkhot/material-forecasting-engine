# Model Card: Construction Material Price Forecaster

## Model Details

- **Developed by:** Vijay Khot
- **Model Architecture:** SARIMAX (Seasonal AutoRegressive Integrated Moving Average).
- **Implementation:** `statsmodels.tsa.statespace.sarimax`.
- **Parameters:** Configured as `(1, 1, 1) x (1, 1, 1, 12)` based on Grid Search optimization.
- **Horizon:** 12-month forward-looking forecast.
- **License:** MIT

## Intended Use

- **Primary Use Case:** Forecasting US Producer Price Indices (PPI) for construction materials (Lumber, Steel, Concrete) to aid in project budgeting.
- **Target Users:** Construction Project Managers, Cost Estimators, and Risk Analysts.
- **Out of Scope:** High-frequency trading or daily price speculation.

## Data Sources

The model ingests monthly economic data (1980–Present) from the **Federal Reserve Economic Data (FRED) API**:

- **Materials:** Steel Mill Products (WPU101702), Softwood Lumber (WPU102), Ready-Mix Concrete (PCU327320327320).
- **Indicators:** Consumer Price Index (CPIAUCSL), Housing Starts (HOUST), Federal Funds Rate (FEDFUNDS).
- **Preprocessing:** Data is resampled to monthly frequency (MS) and missing values are forward-filled (ffill).

## The Engineering Journey: A Search for the Best Predictor

Our journey to find the most accurate forecasting model unfolded in five distinct stages, with each phase challenging the previous leader.

### Round 1: Setting the Baseline

We began by establishing a performance floor using simple heuristics (**Naive**, **Seasonal Naive**, and **Moving Average**).

- **Result:** These models failed to adapt to post-2020 market volatility, confirming that advanced modeling was necessary.

### Round 2: The Classical Contender (Exponential Smoothing)

We introduced **Holt-Winters Exponential Smoothing**.

- **Performance:** It outperformed baselines by capturing strong seasonal patterns (especially in Lumber).
- **Status:** It became the "Champion to Beat."

### Round 3: The Modern Challenger (Prophet)

We tested **Meta's Prophet**, hoping its flexibility with outliers would handle pandemic-era price spikes better.

- **Surprise:** Prophet struggled to match the accuracy of Exponential Smoothing on this specific dataset, often over-smoothing recent cooling trends.

### Round 4: The Hypothesis Test (External Regressors)

We hypothesized that adding economic indicators (Housing Starts, Interest Rates) would improve accuracy.

- **The Experiment:** We trained multivariate versions of Prophet using these exogenous variables.
- **The Finding:** Surprisingly, these models **underperformed** their univariate counterparts. The external variables introduced more noise than signal for short-term forecasting, proving that price history itself held the strongest predictive power.

### Round 5: Enter SARIMAX (The Winner)

In the final phase, we introduced **SARIMAX** as a pure, univariate model.

- **Why it Won:** Unlike Prophet's rigid trend assumptions, SARIMAX's autoregressive terms allowed it to rapidly adapt to recent market corrections. It captured the complex seasonality that Exponential Smoothing found, but with superior error minimization.

## Final Performance Metrics

Models were validated using **Rolling-Origin Cross-Validation** (5 splits) to ensure robustness against different economic regimes.

| Material | Mean sMAPE | Verdict |
| :--- | :--- | :--- |
| **Steel** | ~9.08% | Highly Accurate |
| **Concrete** | ~3.50% | Excellent Stability |
| **Lumber** | ~12.4% | Volatile (Due to high market elasticity) |

## Limitations

- **Univariate Dependence:** The current model relies primarily on historical price action. It does not ingest real-time geopolitical news or supply chain shock data.
- **Black Swan Events:** Like all statistical models, it cannot predict extreme outliers caused by unprecedented global events (e.g., Pandemic shutdowns) unless reflected in recent training data.
