import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Tuple

def select_decision_time_forecasts(
    forecasts_df: pd.DataFrame, 
    cutoff_hour: int = 9, 
    horizon_hours: Optional[int] = None
) -> pd.DataFrame:
    """
    For each startTime, select the latest forecast available before the cutoff on D-1
    or at least H hours before startTime.
    """
    df = forecasts_df.copy()
    df['startTime'] = pd.to_datetime(df['startTime'])
    df['publishTime'] = pd.to_datetime(df['publishTime'])
    
    if horizon_hours is not None:
        # Horizon mode: publishTime <= startTime - H hours
        # Find latest publishTime for each startTime meeting this condition
        df = df[df['publishTime'] <= (df['startTime'] - pd.Timedelta(hours=horizon_hours))]
    else:
        # Decision-time mode: publishTime <= cutoff (09:00) on D-1
        # Create a cutoff column for each startTime
        def get_cutoff(st):
            d_minus_1 = st.date() - timedelta(days=1)
            return datetime.combine(d_minus_1, datetime.min.time()).replace(hour=cutoff_hour)
        
        df['cutoff'] = df['startTime'].apply(get_cutoff)
        df = df[df['publishTime'] <= df['cutoff']]
    
    # Now for each startTime, take the one with the maximum publishTime
    # Sort by startTime and publishTime descending, then take first
    df = df.sort_values(by=['startTime', 'publishTime'], ascending=[True, False])
    selected = df.drop_duplicates(subset=['startTime'], keep='first')
    
    return selected[['startTime', 'publishTime', 'generation']]
