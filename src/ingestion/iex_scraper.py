import os
import asyncio
import logging
from datetime import datetime, date
import pandas as pd
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_DIR  = os.path.join(ROOT_DIR, 'data', 'market')
OUTPUT_PATH = os.path.join(OUTPUT_DIR, 'iex_prices.csv')

async def extract_price_from_page(page, url):
    """Navigates to URL and extracts the 96-block average MCP price."""
    logger.info(f"Navigating to {url}...")
    try:
        await page.goto(url, timeout=60000)
        await page.wait_for_load_state('networkidle')
        await page.wait_for_timeout(5000)
        
        logger.info(f"Parsing DOM tables from {url}...")
        rows = await page.locator('tr').all_inner_texts()
        
        prices = []
        for row in rows:
            parts = row.strip().split('\t')
            if len(parts) >= 6:
                try:
                    val_str = parts[-1].replace('Rs', '').replace(',', '').replace('₹', '').strip()
                    price = float(val_str)
                    if 0 <= price <= 20000:
                        prices.append(price)
                except Exception:
                    continue
        
        if prices:
            avg_price = sum(prices) / len(prices)
            logger.info(f"Successfully calculated average price from {len(prices)} blocks: {avg_price}")
            return avg_price
        else:
            logger.warning(f"Could not find valid price blocks on {url}.")
            return None
    except Exception as e:
        logger.error(f"Error scraping {url}: {e}")
        return None

async def scrape_iex_data():
    """Scrape real-time DAM and RTM prices from IEX website using Playwright."""
    data_payload = {}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        # 1. Scrape DAM
        dam_url = 'https://www.iexindia.com/market-data/day-ahead-market/market-snapshot'
        dam_price = await extract_price_from_page(page, dam_url)
        if dam_price:
            data_payload['dam_price_rs_mwh'] = dam_price
            
        # 2. Scrape RTM
        rtm_url = 'https://www.iexindia.com/market-data/real-time-market/market-snapshot'
        rtm_price = await extract_price_from_page(page, rtm_url)
        if rtm_price:
            data_payload['rtm_price_rs_mwh'] = rtm_price
            
        await browser.close()
            
    return data_payload if data_payload else None

def process_and_save(scraped_data):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    if os.path.exists(OUTPUT_PATH):
        df = pd.read_csv(OUTPUT_PATH)
        df['date'] = pd.to_datetime(df['date'])
    else:
        logger.warning("No existing IEX data found. Running generator to backfill.")
        from src.ingestion.iex_price_generator import main as gen_historical
        gen_historical()
        df = pd.read_csv(OUTPUT_PATH)
        df['date'] = pd.to_datetime(df['date'])

    today_date = date.today()
    dam_price = None
    rtm_price = None
    
    if scraped_data:
        dam_price = scraped_data.get('dam_price_rs_mwh')
        rtm_price = scraped_data.get('rtm_price_rs_mwh')
    
    if not dam_price:
        logger.warning("DAM Scraping failed. Using 7-day rolling average as fallback.")
        recent_dam = df['dam_price_rs_mwh'].tail(7)
        dam_price = recent_dam.mean() if len(recent_dam) > 0 else 4500

    if not rtm_price:
        logger.warning("RTM Scraping failed. Calculating RTM proxy from DAM.")
        rtm_price = dam_price * 1.03 # Rough proxy

    peak_price   = dam_price * 1.25
    offpeak_price = dam_price * 0.85
    vwap = (peak_price * 12 + offpeak_price * 12) / 24

    new_row = {
        'date'            : today_date,
        'dam_price_rs_mwh': round(dam_price, 2),
        'rtm_price_rs_mwh': round(rtm_price, 2),
        'peak_price'      : round(peak_price, 2),
        'offpeak_price'   : round(offpeak_price, 2),
        'vwap_rs_mwh'     : round(vwap, 2),
        'month'           : today_date.month,
        'year'            : today_date.year,
        'day_of_week'     : today_date.strftime('%a'),
    }

    df = df[df['date'].dt.date != today_date]
    new_df = pd.DataFrame([new_row])
    new_df['date'] = pd.to_datetime(new_df['date'])
    df = pd.concat([df, new_df], ignore_index=True)
    
    df.to_csv(OUTPUT_PATH, index=False)
    logger.info(f"Saved real-time data for {today_date}: DAM ₹{dam_price:,.2f}/MWh | RTM ₹{rtm_price:,.2f}/MWh -> {OUTPUT_PATH}")

def main():
    logger.info("=" * 55)
    logger.info("IEX Playwright Scraper — Starting")
    logger.info("=" * 55)
    
    try:
        data = asyncio.run(scrape_iex_data())
        process_and_save(data)
    except Exception as e:
        logger.error(f"Critical error in scraper: {e}")
        process_and_save(None)

    logger.info("=" * 55)
    logger.info("IEX Playwright Scraper — Completed")
    logger.info("=" * 55)

if __name__ == "__main__":
    main()
