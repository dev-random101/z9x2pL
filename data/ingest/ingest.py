import httpx
import pandas as pd
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional
import os

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1"

async def fetch_with_retry(client: httpx.AsyncClient, url: str, params: dict, retries: int = 3, backoff: float = 1.0):
    for i in range(retries):
        try:
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            if i == retries - 1:
                logger.error(f"Failed to fetch {url} after {retries} retries: {e}")
                raise
            wait = backoff * (2 ** i)
            logger.warning(f"Retry {i+1}/{retries} for {url} in {wait:.2f}s due to: {e}")
            await asyncio.sleep(wait)

async def ingest_actuals(client: httpx.AsyncClient, start_date: str, end_date: str):
    """
    Fetch FUELHH data for WIND.
    """
    logger.info(f"Ingesting actuals from {start_date} to {end_date}...")
    url = f"{BASE_URL}/FUELHH"
    params = {
        "from": start_date,
        "to": end_date,
        "fuelType": "WIND"
    }
    
    # The API might limit date ranges. For Jan 2026, we do it in chunks if needed.
    # For now, we try the whole month.
    data = await fetch_with_retry(client, url, params)
    df = pd.DataFrame(data)
    
    if df.empty:
        logger.warning("No actuals data found.")
        return df

    # Clean and validate
    # Expected fields: startTime, generation
    df['startTime'] = pd.to_datetime(df['startTime'])
    df['generation'] = pd.to_numeric(df['generation'], errors='coerce')
    
    return df[['startTime', 'generation']]

async def ingest_forecasts(client: httpx.AsyncClient, start_date: str, end_date: str):
    """
    Fetch WINDFOR data.
    """
    logger.info(f"Ingesting forecasts from {start_date} to {end_date}...")
    url = f"{BASE_URL}/WINDFOR"
    params = {
        "from": start_date,
        "to": end_date
    }
    
    data = await fetch_with_retry(client, url, params)
    df = pd.DataFrame(data)
    
    if df.empty:
        logger.warning("No forecast data found.")
        return df

    # Clean and validate
    # Expected fields: startTime, publishTime, generation
    df['startTime'] = pd.to_datetime(df['startTime'])
    df['publishTime'] = pd.to_datetime(df['publishTime'])
    df['generation'] = pd.to_numeric(df['generation'], errors='coerce')
    
    return df[['startTime', 'publishTime', 'generation']]

async def main():
    # Dates for January 2026
    # Actuals: Jan 2026
    # Forecasts: Late Dec 2025 to Jan 2026 to capture forecasts for Jan 1
    actuals_start = "2026-01-01"
    actuals_end = "2026-01-31"
    
    forecasts_start = "2025-12-20"
    forecasts_end = "2026-01-31"
    
    async with httpx.AsyncClient() as client:
        try:
            actuals_df = await ingest_actuals(client, actuals_start, actuals_end)
            forecasts_df = await ingest_forecasts(client, forecasts_start, forecasts_end)
            
            # Save processed data
            os.makedirs("data/processed", exist_ok=True)
            
            if not actuals_df.empty:
                actuals_df.to_csv("data/processed/actuals.csv", index=False)
                logger.info(f"Saved actuals to data/processed/actuals.csv ({len(actuals_df)} rows)")
            
            if not forecasts_df.empty:
                forecasts_df.to_csv("data/processed/forecasts.csv", index=False)
                logger.info(f"Saved forecasts to data/processed/forecasts.csv ({len(forecasts_df)} rows)")
                
        except Exception as e:
            logger.exception(f"Ingestion failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
