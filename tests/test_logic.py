import pytest
import pandas as pd
from datetime import datetime, timedelta
from services.selection import select_decision_time_forecasts
from services.metrics import calculate_metrics

def test_decision_time_selection():
    # Setup sample data
    # Target startTime: 2026-01-01 00:00
    # Cutoff: 2025-12-31 09:00
    data = [
        {'startTime': '2026-01-01 00:00', 'publishTime': '2025-12-31 00:00', 'generation': 100},
        {'startTime': '2026-01-01 00:00', 'publishTime': '2025-12-31 08:00', 'generation': 110}, # Latest before cutoff
        {'startTime': '2026-01-01 00:00', 'publishTime': '2025-12-31 10:00', 'generation': 120}, # After cutoff
    ]
    df = pd.DataFrame(data)
    
    # Test Decision-time mode
    selected = select_decision_time_forecasts(df, cutoff_hour=9)
    assert len(selected) == 1
    assert selected.iloc[0]['generation'] == 110
    
    # Test Horizon mode (H=24 hours)
    # For 2026-01-01 00:00, latest before 2025-12-31 00:00
    selected_h = select_decision_time_forecasts(df, horizon_hours=24)
    assert len(selected_h) == 1
    assert selected_h.iloc[0]['generation'] == 100

def test_metrics_calculation():
    actuals = pd.DataFrame({
        'startTime': pd.to_datetime(['2026-01-01 00:00', '2026-01-01 00:30']),
        'generation': [1000, 2000]
    })
    forecasts = pd.DataFrame({
        'startTime': pd.to_datetime(['2026-01-01 00:00', '2026-01-01 00:30']),
        'publishTime': pd.to_datetime(['2025-12-31 09:00', '2025-12-31 09:00']),
        'generation': [1100, 1900] # Error: +100, -100
    })
    
    metrics = calculate_metrics(actuals, forecasts)
    assert metrics['mae'] == 100
    assert metrics['bias'] == 0
    assert metrics['p90'] > 0
