import pandas as pd
import numpy as np
from typing import Dict, Any

def calculate_metrics(actuals_df: pd.DataFrame, forecasts_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate forecast accuracy metrics.
    Error = Forecast - Actual (Positive bias means over-forecast)
    """
    # Inner join on startTime
    merged = pd.merge(actuals_df, forecasts_df, on='startTime', suffixes=('_act', '_fc'))
    
    if merged.empty:
        return {"error": "No overlapping data found"}
    
    # Calculation logic
    actual = merged['generation_act']
    forecast = merged['generation_fc']
    error = forecast - actual
    abs_error = error.abs()
    
    mae = abs_error.mean()
    rmse = np.sqrt((error**2).mean())
    bias = error.mean()
    
    # MAPE Guard: Use Mean Absolute Percentage Error (MAPE) or Normalized MAE
    # Using Normalized MAE: MAE / mean(Actual)
    mean_actual = actual.mean()
    nmae = mae / mean_actual if mean_actual != 0 else np.nan
    
    p50 = abs_error.quantile(0.5)
    p90 = abs_error.quantile(0.9)
    p95 = abs_error.quantile(0.95)
    
    coverage = len(merged) / len(actuals_df) * 100 if len(actuals_df) > 0 else 0
    
    # Plain-language insight
    bias_dir = "over-predicts" if bias > 0 else "under-predicts"
    insight = (
        f"Forecast {bias_dir} by {abs(bias):.2f} MW on average. "
        f"Covering 90% of cases requires a buffer of {p90:.2f} MW."
    )
    
    return {
        "mae": mae,
        "rmse": rmse,
        "bias": bias,
        "nmae": nmae,
        "p50": p50,
        "p90": p90,
        "p95": p95,
        "coverage": coverage,
        "insight": insight
    }

def calculate_metrics_by_hour(actuals_df: pd.DataFrame, forecasts_df: pd.DataFrame) -> pd.DataFrame:
    merged = pd.merge(actuals_df, forecasts_df, on='startTime', suffixes=('_act', '_fc'))
    merged['hour'] = merged['startTime'].dt.hour
    merged['error'] = merged['generation_fc'] - merged['generation_act']
    
    return merged.groupby('hour')['error'].agg(['mean', 'std', 'count']).reset_index()

def calculate_metrics_by_horizon(forecasts_df: pd.DataFrame, actuals_df: pd.DataFrame) -> pd.DataFrame:
    # Horizon = startTime - publishTime
    merged = pd.merge(forecasts_df, actuals_df, on='startTime', suffixes=('_fc', '_act'))
    merged['horizon_hours'] = (merged['startTime'] - merged['publishTime']).dt.total_seconds() / 3600
    merged['error'] = merged['generation_fc'] - merged['generation_act']
    
    return merged.groupby('horizon_hours')['error'].agg(['mean', 'std', 'count']).reset_index()
