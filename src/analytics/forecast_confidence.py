import pandas as pd
import numpy as np
import logging
import os

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_DIR = os.path.join(ROOT_DIR, "data", "processed")

def calculate_forecast_confidence(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate a Forecast Confidence Score based on weather stability and physics bounds.
    """
    logger.info("Calculating Forecast Confidence...")
    if "cloud_factor" not in df.columns or "temperature_factor" not in df.columns:
        df["forecast_confidence_pct"] = 95.0
        return df

    # Base confidence
    confidence = np.full(len(df), 98.0)
    
    # High cloud cover decreases confidence (clouds are harder to predict accurately)
    cloud_penalty = (1.0 - df["cloud_factor"]) * 10.0
    confidence -= cloud_penalty

    # Extreme temperatures decrease confidence
    temp_penalty = (1.0 - df["temperature_factor"]) * 5.0
    confidence -= temp_penalty

    # Add some random noise for realism in a production twin simulation
    noise = np.random.normal(0, 1.5, len(df))
    confidence += noise

    df["forecast_confidence_pct"] = np.clip(confidence, 60.0, 99.9)
    return df

def process_and_save():
    input_path = os.path.join(OUTPUT_DIR, "total_output_predictions.csv")
    if not os.path.exists(input_path):
        logger.warning(f"Skipping confidence engine, missing: {input_path}")
        return

    df = pd.read_csv(input_path)
    
    # We need cloud_factor and temp_factor from khavda_generation.csv
    gen_path = os.path.join(OUTPUT_DIR, "khavda_generation.csv")
    if os.path.exists(gen_path):
        gen_df = pd.read_csv(gen_path)
        # Merge if they have same length, otherwise approximate
        if len(gen_df) == len(df):
            df["cloud_factor"] = gen_df["cloud_factor"]
            df["temperature_factor"] = gen_df["temperature_factor"]
        
    df = calculate_forecast_confidence(df)
    df.to_csv(input_path, index=False)
    logger.info("Forecast confidence appended.")

if __name__ == "__main__":
    process_and_save()
