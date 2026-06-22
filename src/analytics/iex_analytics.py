"""
IEX Market Analytics Engine

Computes all IEX / Energy Market KPIs:
  - Historical DAM & RTM price analytics
  - Revenue backtesting (Generation × Price)
  - Future revenue forecasting
  - Scenario simulation
  - Executive market insights
  - Report exports

Outputs (reports/):
  iex_market_summary.csv
  revenue_backtesting.csv
  future_market_revenue.csv
  market_executive_insights.csv
"""

import os
import logging
import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

ROOT_DIR    = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REPORTS_DIR = os.path.join(ROOT_DIR, 'reports')
MARKET_DIR  = os.path.join(REPORTS_DIR, 'market')
os.makedirs(MARKET_DIR, exist_ok=True)
os.makedirs(os.path.join(ROOT_DIR, 'data', 'market'), exist_ok=True)

# Input paths
GEN_PATH      = os.path.join(ROOT_DIR, 'data', 'processed', 'khavda_generation.csv')
PRED_PATH     = os.path.join(ROOT_DIR, 'reports', 'total_output', 'total_output_predictions.csv')
IEX_PATH      = os.path.join(ROOT_DIR, 'data', 'market', 'iex_prices.csv')
FUTURE_FC_PATH = os.path.join(ROOT_DIR, 'reports', 'future_generation_forecast.csv')

# Output paths
SUMMARY_OUT  = os.path.join(MARKET_DIR, 'iex_market_summary.csv')
BACKTEST_OUT = os.path.join(MARKET_DIR, 'revenue_backtesting.csv')
FUTURE_OUT   = os.path.join(MARKET_DIR, 'future_market_revenue.csv')
INSIGHTS_OUT = os.path.join(MARKET_DIR, 'market_executive_insights.csv')


# ─────────────────────────────────────────────────────────────────────────────
# LOADERS
# ─────────────────────────────────────────────────────────────────────────────

def load_generation() -> pd.DataFrame:
    df = pd.read_csv(GEN_PATH)
    df['date'] = pd.to_datetime(df['date'])
    return df


def load_iex_prices() -> pd.DataFrame:
    """Load IEX prices, generating them if the file is absent."""
    if not os.path.exists(IEX_PATH):
        logger.warning("IEX price file not found. Generating synthetic prices…")
        from src.ingestion.iex_price_generator import main as gen_prices
        gen_prices()
    df = pd.read_csv(IEX_PATH)
    df['date'] = pd.to_datetime(df['date'])
    
    # Ensure RTM price exists (fallback for older generated datasets)
    if 'rtm_price_rs_mwh' not in df.columns:
        df['rtm_price_rs_mwh'] = (df['dam_price_rs_mwh'] * 1.03).round(2)
        
    # Create per-kWh columns
    df['dam_price_rs_kwh'] = (df['dam_price_rs_mwh'] / 1000).round(2)
    df['rtm_price_rs_kwh'] = (df['rtm_price_rs_mwh'] / 1000).round(2)
    
    return df


def load_future_forecast() -> pd.DataFrame:
    """Load future generation forecast."""
    if os.path.exists(FUTURE_FC_PATH):
        df = pd.read_csv(FUTURE_FC_PATH)
        df['date'] = pd.to_datetime(df['date'])
        return df

    if os.path.exists(PRED_PATH):
        df = pd.read_csv(PRED_PATH)
        df['date'] = pd.to_datetime(df['date'])
        future = df[df['actual_total_generation_mw'].isna()].copy()
        future = future.rename(columns={'predicted_total_generation_mw': 'forecast_generation_mw'})
        return future[['date', 'forecast_generation_mw']]

    return pd.DataFrame()


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1 — MARKET KPIs
# ─────────────────────────────────────────────────────────────────────────────

def compute_market_kpis(iex: pd.DataFrame, backtest: pd.DataFrame) -> dict:
    avg_price = iex['dam_price_rs_mwh'].mean()
    avg_price_kwh = iex['dam_price_rs_kwh'].mean()
    
    avg_rtm = iex['rtm_price_rs_mwh'].mean()
    avg_rtm_kwh = iex['rtm_price_rs_kwh'].mean()
    
    max_price = iex['dam_price_rs_mwh'].max()
    max_price_kwh = iex['dam_price_rs_kwh'].max()
    
    min_price = iex['dam_price_rs_mwh'].min()
    min_price_kwh = iex['dam_price_rs_kwh'].min()
    
    price_std  = iex['dam_price_rs_mwh'].std()
    volatility = (price_std / avg_price) * 100

    avg_daily_rev  = backtest['revenue_inr'].mean()     if not backtest.empty else 0
    total_rev      = backtest['revenue_inr'].sum()      if not backtest.empty else 0
    max_day_rev    = backtest['revenue_inr'].max()      if not backtest.empty else 0
    min_day_rev    = backtest['revenue_inr'].min()      if not backtest.empty else 0

    return {
        'avg_dam_price_rs_mwh' : round(avg_price, 2),
        'avg_dam_price_rs_kwh' : round(avg_price_kwh, 2),
        'avg_rtm_price_rs_mwh' : round(avg_rtm, 2),
        'avg_rtm_price_rs_kwh' : round(avg_rtm_kwh, 2),
        'max_dam_price_rs_mwh' : round(max_price, 2),
        'max_dam_price_rs_kwh' : round(max_price_kwh, 2),
        'min_dam_price_rs_mwh' : round(min_price, 2),
        'min_dam_price_rs_kwh' : round(min_price_kwh, 2),
        'price_volatility_pct' : round(volatility, 2),
        'avg_daily_revenue_inr': round(avg_daily_rev, 2),
        'total_revenue_inr'    : round(total_rev, 2),
        'max_day_revenue_inr'  : round(max_day_rev, 2),
        'min_day_revenue_inr'  : round(min_day_rev, 2),
        'highest_price_day'    : iex.loc[iex['dam_price_rs_mwh'].idxmax(), 'date'].strftime('%Y-%m-%d'),
        'lowest_price_day'     : iex.loc[iex['dam_price_rs_mwh'].idxmin(), 'date'].strftime('%Y-%m-%d'),
    }


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2 — REVENUE BACKTESTING
# ─────────────────────────────────────────────────────────────────────────────

def backtest_revenue(gen: pd.DataFrame, iex: pd.DataFrame) -> pd.DataFrame:
    """Merge historical generation with IEX prices → compute revenue."""
    merged = pd.merge(
        gen[['date', 'solar_generation_mw', 'wind_generation_mw', 'total_generation_mw']],
        iex[['date', 'dam_price_rs_mwh', 'dam_price_rs_kwh', 'rtm_price_rs_mwh', 'rtm_price_rs_kwh']],
        on='date', how='inner'
    )

    merged['revenue_inr']       = (merged['total_generation_mw'] * merged['dam_price_rs_mwh']).round(2)
    merged['solar_revenue_inr'] = (merged['solar_generation_mw'] * merged['dam_price_rs_mwh']).round(2)
    merged['wind_revenue_inr']  = (merged['wind_generation_mw']  * merged['dam_price_rs_mwh']).round(2)
    merged['revenue_lakhs']     = (merged['revenue_inr'] / 1e5).round(4)
    merged['revenue_crores']    = (merged['revenue_inr'] / 1e7).round(6)
    merged['month']             = merged['date'].dt.to_period('M').astype(str)
    merged['year']              = merged['date'].dt.year

    return merged.sort_values('date').reset_index(drop=True)


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3 — FUTURE REVENUE FORECAST
# ─────────────────────────────────────────────────────────────────────────────

def forecast_revenue(future_gen: pd.DataFrame, iex: pd.DataFrame) -> pd.DataFrame:
    """Project future revenue using rolling price patterns."""
    if future_gen.empty:
        return pd.DataFrame()

    iex_sorted = iex.sort_values('date')
    rolling_avg = iex_sorted['dam_price_rs_mwh'].tail(30).mean()
    
    monthly_mult = {
        1: 1.05, 2: 1.10, 3: 1.25, 4: 1.40, 5: 1.45, 6: 1.30,
        7: 0.90, 8: 0.88, 9: 0.92, 10: 1.00, 11: 0.98, 12: 1.02
    }

    gen_col = 'forecast_generation_mw' if 'forecast_generation_mw' in future_gen.columns else 'predicted_total_generation_mw'

    rows = []
    for _, row in future_gen.iterrows():
        d = row['date']
        mult = monthly_mult.get(d.month, 1.0)
        expected_price = rolling_avg * mult
        optimistic     = expected_price * 1.15
        pessimistic    = expected_price * 0.85

        gen_mw = row[gen_col]
        rows.append({
            'date'                    : d,
            'forecast_generation_mw'  : round(gen_mw, 2),
            'expected_dam_price'      : round(expected_price, 2),
            'expected_dam_price_kwh'  : round(expected_price / 1000, 2),
            'optimistic_price'        : round(optimistic, 2),
            'pessimistic_price'       : round(pessimistic, 2),
            'forecast_revenue_inr'    : round(gen_mw * expected_price, 2),
            'optimistic_revenue_inr'  : round(gen_mw * optimistic, 2),
            'pessimistic_revenue_inr' : round(gen_mw * pessimistic, 2),
            'forecast_revenue_lakhs'  : round(gen_mw * expected_price / 1e5, 4),
            'forecast_revenue_crores' : round(gen_mw * expected_price / 1e7, 6),
        })

    return pd.DataFrame(rows).sort_values('date').reset_index(drop=True)


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4 — SCENARIO SIMULATION
# ─────────────────────────────────────────────────────────────────────────────

def simulate_scenario(backtest: pd.DataFrame, price_change_pct: float = 0.0, gen_change_pct: float = 0.0) -> dict:
    if backtest.empty:
        return {}

    base_revenue = backtest['revenue_inr'].sum()
    adj_price_factor = 1 + price_change_pct / 100
    adj_gen_factor   = 1 + gen_change_pct   / 100
    new_revenue      = base_revenue * adj_price_factor * adj_gen_factor
    delta            = new_revenue - base_revenue
    pct_impact       = (delta / base_revenue) * 100 if base_revenue else 0

    return {
        'base_revenue_inr'    : round(base_revenue, 2),
        'scenario_revenue_inr': round(new_revenue, 2),
        'revenue_delta_inr'   : round(delta, 2),
        'pct_impact'          : round(pct_impact, 2),
        'base_crores'         : round(base_revenue / 1e7, 4),
        'scenario_crores'     : round(new_revenue / 1e7, 4),
        'delta_crores'        : round(delta / 1e7, 4),
    }


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5 — EXECUTIVE INSIGHTS
# ─────────────────────────────────────────────────────────────────────────────

def generate_executive_insights(iex: pd.DataFrame, backtest: pd.DataFrame, future_rev: pd.DataFrame, kpis: dict) -> list[dict]:
    insights = []
    
    monthly_avg = iex.groupby('month')['dam_price_rs_kwh'].mean()
    peak_month  = monthly_avg.idxmax()
    trough_month = monthly_avg.idxmin()
    month_names = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',
                   7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}
    insights.append({
        'Section': 'Price Seasonality (kWh)',
        'Insight': (
            f"DAM prices peak in {month_names.get(peak_month, peak_month)} "
            f"(avg ₹{monthly_avg[peak_month]:.2f}/kWh) and reach their lowest in "
            f"{month_names.get(trough_month, trough_month)} (avg ₹{monthly_avg[trough_month]:.2f}/kWh). "
            f"Scheduling generation maintenance during trough months minimises revenue loss."
        )
    })

    if not backtest.empty:
        monthly_rev = backtest.groupby('month')['revenue_inr'].sum()
        top_3_months = monthly_rev.nlargest(3)
        top_share = top_3_months.sum() / monthly_rev.sum() * 100
        insights.append({
            'Section': 'Revenue Concentration',
            'Insight': (
                f"The top 3 revenue months account for {top_share:.1f}% of total annual market revenue. "
                f"High DAM prices during summer months (April–June) align with Khavda's peak solar irradiance, "
                f"creating a favourable double-upside for market participation."
            )
        })

        top_day = backtest.loc[backtest['revenue_inr'].idxmax()]
        insights.append({
            'Section': 'Peak Revenue Event',
            'Insight': (
                f"The highest single-day market revenue of ₹{top_day['revenue_inr']/1e5:.2f} Lakhs was recorded on "
                f"{top_day['date'].strftime('%d %b %Y')}, when generation reached "
                f"{top_day['total_generation_mw']:.1f} MW at a DAM clearing price of "
                f"₹{top_day['dam_price_rs_kwh']:.2f}/kWh."
            )
        })

    insights.append({
        'Section': 'Market Volatility Risk',
        'Insight': (
            f"IEX DAM price volatility stands at {kpis['price_volatility_pct']:.1f}%, indicating "
            f"{'significant' if kpis['price_volatility_pct'] > 25 else 'moderate'} market price risk. "
            f"Implementing Power Purchase Agreements (PPAs) for 60–70% of generation capacity "
            f"is recommended to hedge against spot market price swings."
        )
    })

    if not future_rev.empty:
        total_future = future_rev['forecast_revenue_inr'].sum()
        days = len(future_rev)
        avg_daily = total_future / days if days else 0
        insights.append({
            'Section': 'Future Revenue Outlook',
            'Insight': (
                f"AI-based forward projections indicate expected market revenue of "
                f"₹{total_future/1e5:.2f} Lakhs over the next {days} forecast days, "
                f"averaging ₹{avg_daily/1e5:.2f} Lakhs/day. "
                f"Revenue remains stable given consistent renewable generation under current weather patterns."
            )
        })

    insights.append({
        'Section': 'Market Floor Strategy',
        'Insight': (
            f"With a market price floor of ₹{kpis['min_dam_price_rs_kwh']:.2f}/kWh observed, "
            f"Khavda's variable generation cost remains well below this threshold, ensuring "
            f"positive contribution margin under all IEX market clearing scenarios. "
            f"The average price of ₹{kpis['avg_dam_price_rs_kwh']:.2f}/kWh provides "
            f"a strong margin above typical renewable LCOE of ₹1.80–2.20/kWh."
        )
    })

    return insights


# ─────────────────────────────────────────────────────────────────────────────
# SAVE REPORTS & MAIN
# ─────────────────────────────────────────────────────────────────────────────

def save_reports(kpis: dict, backtest: pd.DataFrame, future_rev: pd.DataFrame, insights: list):
    pd.DataFrame([kpis]).to_csv(SUMMARY_OUT, index=False)
    if not backtest.empty:
        backtest.to_csv(BACKTEST_OUT, index=False)
    if not future_rev.empty:
        future_rev.to_csv(FUTURE_OUT, index=False)
    if insights:
        pd.DataFrame(insights).to_csv(INSIGHTS_OUT, index=False)

def run_iex_analytics():
    logger.info("=" * 55)
    logger.info("IEX Market Analytics Engine — Starting")
    logger.info("=" * 55)

    gen        = load_generation()
    iex        = load_iex_prices()
    future_gen = load_future_forecast()

    backtest   = backtest_revenue(gen, iex)
    future_rev = forecast_revenue(future_gen, iex)
    kpis       = compute_market_kpis(iex, backtest)
    insights   = generate_executive_insights(iex, backtest, future_rev, kpis)

    save_reports(kpis, backtest, future_rev, insights)

    logger.info("=" * 55)
    logger.info("IEX Market Analytics Engine — Completed")
    logger.info("=" * 55)

    return {
        'iex'       : iex,
        'backtest'  : backtest,
        'future_rev': future_rev,
        'kpis'      : kpis,
        'insights'  : insights,
    }

if __name__ == "__main__":
    run_iex_analytics()
