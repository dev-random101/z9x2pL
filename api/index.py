from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
from datetime import datetime
import os

from services.selection import select_decision_time_forecasts
from services.metrics import calculate_metrics, calculate_metrics_by_hour, calculate_metrics_by_horizon

app = FastAPI(title="UK Wind Generation Analysis API")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load data once at module level for performance
ACTUALS_PATH = "data/processed/actuals.csv"
FORECASTS_PATH = "data/processed/forecasts.csv"

def load_actuals():
    if not os.path.exists(ACTUALS_PATH):
        return pd.DataFrame()
    return pd.read_csv(ACTUALS_PATH, parse_dates=['startTime'])

def load_forecasts():
    if not os.path.exists(FORECASTS_PATH):
        return pd.DataFrame()
    return pd.read_csv(FORECASTS_PATH, parse_dates=['startTime', 'publishTime'])

@app.get("/api/health")
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

@app.get("/api/actuals")
async def get_actuals(start: str, end: str):
    df = load_actuals()
    if df.empty:
        raise HTTPException(status_code=404, detail="No actuals data available")
    
    mask = (df['startTime'] >= start) & (df['startTime'] <= end)
    filtered = df.loc[mask]
    
    return filtered.assign(startTime=filtered['startTime'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')).to_dict(orient='records')

@app.get("/api/forecast")
async def get_forecast(
    start: str, 
    end: str, 
    cutoff_hour: int = Query(9), 
    horizon_hours: Optional[int] = Query(None)
):
    df_all_fc = load_forecasts()
    if df_all_fc.empty:
        raise HTTPException(status_code=404, detail="No forecast data available")
    
    # 1. Selection logic
    selected = select_decision_time_forecasts(df_all_fc, cutoff_hour=cutoff_hour, horizon_hours=horizon_hours)
    
    # 2. Filter by date range
    mask = (selected['startTime'] >= start) & (selected['startTime'] <= end)
    filtered = selected.loc[mask]
    
    # Format dates for JSON
    res = filtered.copy()
    res['startTime'] = res['startTime'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    res['publishTime'] = res['publishTime'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    return res.to_dict(orient='records')

@app.get("/api/metrics")
async def get_metrics(
    start: str, 
    end: str, 
    cutoff_hour: int = Query(9), 
    horizon_hours: Optional[int] = Query(None)
):
    df_act = load_actuals()
    df_fc_all = load_forecasts()
    
    if df_act.empty or df_fc_all.empty:
        raise HTTPException(status_code=404, detail="Data missing for metrics calculation")
    
    # 1. Select decision-time forecasts
    selected_fc = select_decision_time_forecasts(df_fc_all, cutoff_hour=cutoff_hour, horizon_hours=horizon_hours)
    
    # 2. Filter both by date range
    mask_act = (df_act['startTime'] >= start) & (df_act['startTime'] <= end)
    df_act_filtered = df_act.loc[mask_act]
    
    mask_fc = (selected_fc['startTime'] >= start) & (selected_fc['startTime'] <= end)
    df_fc_filtered = selected_fc.loc[mask_fc]
    
    metrics = calculate_metrics(df_act_filtered, df_fc_filtered)
    return metrics

@app.get("/api/metrics/by-hour")
async def get_metrics_by_hour(
    start: str, 
    end: str, 
    cutoff_hour: int = Query(9), 
    horizon_hours: Optional[int] = Query(None)
):
    df_act = load_actuals()
    df_fc_all = load_forecasts()
    
    selected_fc = select_decision_time_forecasts(df_fc_all, cutoff_hour=cutoff_hour, horizon_hours=horizon_hours)
    
    mask_act = (df_act['startTime'] >= start) & (df_act['startTime'] <= end)
    df_act_filtered = df_act.loc[mask_act]
    
    mask_fc = (selected_fc['startTime'] >= start) & (selected_fc['startTime'] <= end)
    df_fc_filtered = selected_fc.loc[mask_fc]
    
    return calculate_metrics_by_hour(df_act_filtered, df_fc_filtered).to_dict(orient='records')

@app.get("/api/metrics/by-horizon")
async def get_metrics_by_horizon(
    start: str, 
    end: str, 
    cutoff_hour: int = Query(9), 
    horizon_hours: Optional[int] = Query(None)
):
    # This one analyzes the raw forecasts vs actuals to see how error changes with horizon
    df_act = load_actuals()
    df_fc_all = load_forecasts()
    
    mask_act = (df_act['startTime'] >= start) & (df_act['startTime'] <= end)
    df_act_filtered = df_act.loc[mask_act]
    
    mask_fc = (df_fc_all['startTime'] >= start) & (df_fc_all['startTime'] <= end)
    df_fc_filtered = df_fc_all.loc[mask_fc]
    
    return calculate_metrics_by_horizon(df_fc_filtered, df_act_filtered).to_dict(orient='records')
