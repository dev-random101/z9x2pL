import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_mock_data():
    print("Generating mock data for January 2026...")
    
    # Time range: Jan 1 to Jan 31, 2026, every 30 mins
    start_time = datetime(2026, 1, 1)
    end_time = datetime(2026, 1, 31, 23, 30)
    times = pd.date_range(start=start_time, end=end_time, freq='30min')
    
    # 1. Actuals (FUELHH)
    # Wind generation roughly 0 to 20,000 MW
    actuals = pd.DataFrame({
        'startTime': times,
        'generation': np.random.uniform(1000, 18000, size=len(times))
    })
    
    # 2. Forecasts (WINDFOR)
    # For each startTime, generate multiple forecasts published at different times
    forecast_rows = []
    for t in times:
        # Generate 3 forecasts for each half-hour
        # Forecast 1: 48 hours before
        # Forecast 2: 24 hours before
        # Forecast 3: 12 hours before ( Decision-time target)
        for horizon in [48, 24, 12]:
            publish_time = t - timedelta(hours=horizon)
            # Forecast = Actual + noise
            actual_val = actuals.loc[actuals['startTime'] == t, 'generation'].values[0]
            noise = np.random.normal(0, 500) 
            forecast_rows.append({
                'startTime': t,
                'publishTime': publish_time,
                'generation': max(0, actual_val + noise)
            })
            
    forecasts = pd.DataFrame(forecast_rows)
    
    # Save processed data
    os.makedirs("data/processed", exist_ok=True)
    actuals.to_csv("data/processed/actuals.csv", index=False)
    forecasts.to_csv("data/processed/forecasts.csv", index=False)
    
    print(f"Saved actuals: {len(actuals)} rows")
    print(f"Saved forecasts: {len(forecasts)} rows")

if __name__ == "__main__":
    generate_mock_data()
