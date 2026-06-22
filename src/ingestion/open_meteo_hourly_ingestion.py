"""
Open-Meteo Hourly Data Ingestion Module

Fetches hourly weather + derived hourly generation estimates for:
  - Last 7 days of history (from Open-Meteo Archive API)
  - Next 14 days forecast (from Open-Meteo Forecast API)

Hourly generation is derived using physics-based proportioning:
  - Solar: hourly generation proportional to hourly shortwave radiation
  - Wind:  hourly generation proportional to wind_speed^3 (power law)
  - Total: sum of solar + wind

Output: data/raw/khavda_hourly.csv
Columns: datetime, date, hour, solar_generation_mw, wind_generation_mw, total_generation_mw,
         temperature_c, wind_speed_ms, solar_radiation_wm2, cloud_cover_pct, humidity_pct,
         rainfall_mm, is_forecast
"""

import os
import logging
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_PATH = os.path.join(ROOT_DIR, 'data', 'raw', 'khavda_hourly.csv')
DAILY_PRED_PATH = os.path.join(ROOT_DIR, 'reports', 'total_output', 'total_output_predictions.csv')

KHAVDA_LAT = 23.90
KHAVDA_LON = 69.75

# Khavda installed capacity assumptions (MW)
SOLAR_CAPACITY_MW = 30000   # 30 GW solar
WIND_CAPACITY_MW  = 10000   # 10 GW wind

# Efficiency factors
SOLAR_PANEL_EFFICIENCY = 0.18     # 18%
WIND_CAPACITY_FACTOR   = 0.35     # 35% average capacity factor base

HOURLY_PARAMS = [
    "shortwave_radiation",
    "wind_speed_10m",
    "temperature_2m",
    "relative_humidity_2m",
    "cloud_cover",
    "precipitation"
]


def fetch_historical_hourly(start_date: str, end_date: str) -> pd.DataFrame:
    """Fetch hourly historical data from Open-Meteo Archive API."""
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": KHAVDA_LAT,
        "longitude": KHAVDA_LON,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": HOURLY_PARAMS,
        "timezone": "Asia/Kolkata",
        "wind_speed_unit": "ms"
    }
    logger.info(f"Fetching hourly history from {start_date} to {end_date}...")
    r = requests.get(url, params=params, timeout=60)
    r.raise_for_status()
    data = r.json().get('hourly', {})
    df = pd.DataFrame(data)
    df['is_forecast'] = False
    return df


def fetch_forecast_hourly() -> pd.DataFrame:
    """Fetch 14-day hourly forecast from Open-Meteo Forecast API."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": KHAVDA_LAT,
        "longitude": KHAVDA_LON,
        "hourly": HOURLY_PARAMS,
        "timezone": "Asia/Kolkata",
        "wind_speed_unit": "ms",
        "forecast_days": 14
    }
    logger.info("Fetching 14-day hourly forecast...")
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    data = r.json().get('hourly', {})
    df = pd.DataFrame(data)
    df['is_forecast'] = True
    return df


def compute_hourly_generation(df: pd.DataFrame, daily_pred_path: str) -> pd.DataFrame:
    """
    Derive MW-scale hourly solar/wind generation by distributing daily totals
    across hours using the physics signal (radiation / wind_speed^3).
    """
    df = df.copy()
    df['datetime'] = pd.to_datetime(df['time'])
    df['date']     = df['datetime'].dt.date
    df['hour']     = df['datetime'].dt.hour

    # Clean raw weather columns
    df['shortwave_radiation']     = df['shortwave_radiation'].clip(lower=0).fillna(0)
    df['wind_speed_10m']          = df['wind_speed_10m'].clip(lower=0).fillna(0)
    df['temperature_2m']          = df['temperature_2m'].fillna(df['temperature_2m'].mean())
    df['relative_humidity_2m']    = df['relative_humidity_2m'].fillna(50)
    df['cloud_cover']             = df['cloud_cover'].fillna(0)
    df['precipitation']           = df['precipitation'].fillna(0)

    # Load daily predictions to anchor totals
    daily_pred = None
    if os.path.exists(daily_pred_path):
        try:
            daily_pred = pd.read_csv(daily_pred_path)
            daily_pred['date'] = pd.to_datetime(daily_pred['date']).dt.date
        except Exception:
            daily_pred = None

    # ---------- Solar hourly distribution ----------
    # Within each day: hourly_solar = (hourly_radiation / daily_total_radiation) * daily_solar_mw
    df['wind_power_proxy'] = df['wind_speed_10m'] ** 3

    daily_radiation = df.groupby('date')['shortwave_radiation'].transform('sum')
    daily_wind_cube = df.groupby('date')['wind_power_proxy'].transform('sum')

    # Fractions (avoid div-by-zero)
    df['solar_fraction'] = np.where(daily_radiation > 0, df['shortwave_radiation'] / daily_radiation, 0)
    df['wind_fraction']  = np.where(daily_wind_cube > 0, df['wind_power_proxy'] / daily_wind_cube, 1/24)

    def get_daily_total(date, col, default):
        if daily_pred is not None and date in daily_pred['date'].values:
            row = daily_pred[daily_pred['date'] == date].iloc[0]
            return float(row.get(col, default))
        return default

    default_solar = SOLAR_CAPACITY_MW * WIND_CAPACITY_FACTOR * 0.6
    default_wind  = WIND_CAPACITY_MW  * WIND_CAPACITY_FACTOR * 0.4

    # Map daily totals per row
    date_to_solar = {}
    date_to_wind  = {}

    for d in df['date'].unique():
        pred_total = get_daily_total(d, 'predicted_total_generation_mw', default_solar + default_wind)
        # If we have actual from non-null rows, use it for historical
        if daily_pred is not None and d in daily_pred['date'].values:
            row = daily_pred[daily_pred['date'] == d].iloc[0]
            act = row.get('actual_total_generation_mw', np.nan)
            if pd.notna(act) and act > 0:
                pred_total = float(act)
        date_to_solar[d] = pred_total * 0.60
        date_to_wind[d]  = pred_total * 0.40

    df['daily_solar_mw'] = df['date'].map(date_to_solar).fillna(default_solar)
    df['daily_wind_mw']  = df['date'].map(date_to_wind).fillna(default_wind)

    df['solar_generation_mw'] = (df['solar_fraction'] * df['daily_solar_mw']).clip(lower=0).round(2)
    df['wind_generation_mw']  = (df['wind_fraction']  * df['daily_wind_mw']).clip(lower=0).round(2)
    df['total_generation_mw'] = (df['solar_generation_mw'] + df['wind_generation_mw']).round(2)

    # Rename weather columns for consistency
    df = df.rename(columns={
        'shortwave_radiation'  : 'solar_radiation_wm2',
        'wind_speed_10m'       : 'wind_speed_ms',
        'temperature_2m'       : 'temperature_c',
        'relative_humidity_2m' : 'humidity_pct',
        'cloud_cover'          : 'cloud_cover_pct',
        'precipitation'        : 'rainfall_mm',
    })

    output_cols = [
        'datetime', 'date', 'hour',
        'solar_generation_mw', 'wind_generation_mw', 'total_generation_mw',
        'temperature_c', 'wind_speed_ms', 'solar_radiation_wm2',
        'cloud_cover_pct', 'humidity_pct', 'rainfall_mm', 'is_forecast'
    ]
    return df[output_cols].sort_values('datetime').reset_index(drop=True)


def main():
    logger.info("=" * 50)
    logger.info("Starting Open-Meteo Hourly Ingestion")
    logger.info("=" * 50)

    os.makedirs(os.path.join(ROOT_DIR, 'data', 'raw'), exist_ok=True)

    today      = datetime.now().date()
    hist_start = (today - timedelta(days=7)).strftime('%Y-%m-%d')
    hist_end   = today.strftime('%Y-%m-%d')

    # Fetch both historical and forecast
    hist_df     = fetch_historical_hourly(hist_start, hist_end)
    forecast_df = fetch_forecast_hourly()

    # Combine & deduplicate
    combined = pd.concat([hist_df, forecast_df], ignore_index=True)
    combined = combined.drop_duplicates(subset=['time'], keep='first')

    # Derive hourly generation
    final_df = compute_hourly_generation(combined, DAILY_PRED_PATH)

    final_df.to_csv(OUTPUT_PATH, index=False)
    logger.info(f"Saved {len(final_df)} hourly rows to {OUTPUT_PATH}")
    logger.info(f"Date range: {final_df['date'].min()} to {final_df['date'].max()}")
    logger.info("=" * 50)
    logger.info("Hourly Ingestion Completed Successfully")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
