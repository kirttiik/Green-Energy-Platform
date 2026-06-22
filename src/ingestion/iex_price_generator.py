"""
IEX DAM Price Data Generator

Generates realistic IEX Day-Ahead Market (DAM) prices for the Khavda region
based on actual Indian energy market patterns:
  - Seasonal variations (summer peaks, monsoon dips)
  - Time-of-day effects averaged to daily weighted price
  - Market shock events (grid stress, renewable curtailment)
  - Price range: ₹1,800 – ₹12,000 / MWh (₹1.8 – ₹12 / kWh)

Output: data/market/iex_prices.csv
"""

import os
import numpy as np
import pandas as pd
import logging
from datetime import date

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_DIR  = os.path.join(ROOT_DIR, 'data', 'market')
OUTPUT_PATH = os.path.join(OUTPUT_DIR, 'iex_prices.csv')

# ── IEX Market Constants (₹/MWh) ─────────────────────────────────────────────
BASE_PRICE      = 3800   # ₹/MWh base off-peak DAM clearing price
PEAK_PREMIUM    = 2200   # Additional premium during peak months
MIN_FLOOR_PRICE = 1800   # Market floor (variable cost benchmark)
MAX_PRICE       = 12000  # Extreme grid stress price cap

# Monthly seasonality multipliers (Jan=0 … Dec=11)
# Summer (Mar–Jun) = high demand + high prices
# Monsoon (Jul–Sep) = renewable surplus → lower prices
# Winter (Oct–Feb) = moderate
MONTHLY_MULTIPLIER = {
    1:  1.05,   # Jan
    2:  1.10,   # Feb
    3:  1.25,   # Mar
    4:  1.40,   # Apr — summer peak
    5:  1.45,   # May — hottest, max AC load
    6:  1.30,   # Jun — pre-monsoon
    7:  0.90,   # Jul — monsoon, renewable surplus
    8:  0.88,   # Aug — peak monsoon
    9:  0.92,   # Sep — tail-end monsoon
    10: 1.00,   # Oct — post-monsoon
    11: 0.98,   # Nov
    12: 1.02,   # Dec
}

# Day-of-week: weekdays are 5–8% higher than weekends
DOW_MULTIPLIER = {0: 1.06, 1: 1.06, 2: 1.05, 3: 1.05, 4: 1.04, 5: 0.97, 6: 0.96}

# Probability of high-price shock events
SHOCK_PROBABILITY = 0.015   # ~5 events per year
SHOCK_MULTIPLIER  = 2.5


def generate_iex_prices(start_date: str, end_date: str, seed: int = 42) -> pd.DataFrame:
    """Generate synthetic but realistic daily IEX DAM clearing prices."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')

    records = []
    for d in dates:
        month_mult = MONTHLY_MULTIPLIER[d.month]
        dow_mult   = DOW_MULTIPLIER[d.dayofweek]

        # Base price with seasonal / DoW adjustment
        base = BASE_PRICE * month_mult * dow_mult

        # Random daily variation: log-normal (captures market skew)
        noise = rng.lognormal(mean=0, sigma=0.12)
        price = base * noise

        # Shock event
        if rng.random() < SHOCK_PROBABILITY:
            price *= SHOCK_MULTIPLIER

        price = float(np.clip(price, MIN_FLOOR_PRICE, MAX_PRICE))

        # Volume weighted average price (VWAP) proxy: day and night blocks
        peak_price   = float(np.clip(price * rng.uniform(1.15, 1.35), MIN_FLOOR_PRICE, MAX_PRICE))
        offpeak_price = float(np.clip(price * rng.uniform(0.70, 0.88), MIN_FLOOR_PRICE, MAX_PRICE))
        # VWAP: 12 peak hours (06:00–18:00) + 12 off-peak
        vwap = (peak_price * 12 + offpeak_price * 12) / 24

        # RTM (Real-Time Market) price proxy: Usually tracks DAM but with higher volatility
        rtm_noise = rng.normal(loc=1.03, scale=0.08) # ~3% higher on average, with 8% variance
        rtm_price = float(np.clip(price * rtm_noise, MIN_FLOOR_PRICE, MAX_PRICE))


        records.append({
            'date'            : d.date(),
            'dam_price_rs_mwh': round(price, 2),           # Discovered clearing price
            'rtm_price_rs_mwh': round(rtm_price, 2),       # Real-Time Market price
            'peak_price'      : round(peak_price, 2),
            'offpeak_price'   : round(offpeak_price, 2),
            'vwap_rs_mwh'     : round(vwap, 2),
            'month'           : d.month,
            'year'            : d.year,
            'day_of_week'     : d.day_name()[:3],
        })

    return pd.DataFrame(records)


def main():
    logger.info("=" * 55)
    logger.info("IEX DAM Price Generator — Starting")
    logger.info("=" * 55)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Match the historical generation date range
    gen_path = os.path.join(ROOT_DIR, 'data', 'processed', 'khavda_generation.csv')
    if os.path.exists(gen_path):
        gen = pd.read_csv(gen_path)
        gen['date'] = pd.to_datetime(gen['date'])
        start = gen['date'].min().strftime('%Y-%m-%d')
        end   = gen['date'].max().strftime('%Y-%m-%d')
    else:
        start = '2021-06-23'
        end   = date.today().strftime('%Y-%m-%d')

    logger.info(f"Generating IEX prices from {start} to {end}...")
    df = generate_iex_prices(start, end)

    df.to_csv(OUTPUT_PATH, index=False)
    logger.info(f"Saved {len(df)} daily price records → {OUTPUT_PATH}")
    logger.info(f"Price range: ₹{df.dam_price_rs_mwh.min():,.0f} – ₹{df.dam_price_rs_mwh.max():,.0f} / MWh")
    logger.info("=" * 55)
    logger.info("IEX DAM Price Generator — Completed")
    logger.info("=" * 55)


if __name__ == "__main__":
    main()
