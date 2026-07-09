from fastapi import APIRouter

router = APIRouter(
    prefix="/api/weather",
    tags=["Weather Intelligence"]
)

@router.get("/metrics")
def get_weather_metrics():
    # Simulated extraction from data/processed/weather_risk_analytics.csv
    return {
        "current_temperature": 34.5,
        "solar_irradiance": 850.2,
        "wind_speed": 12.4,
        "cloud_cover": "15%",
        "precipitation_risk": "Low",
        "temperature_stress_factor": 0.95
    }

@router.get("/forecast")
def get_weather_forecast():
    # Simulated 7-day forecast
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    import random
    return [
        {
            "day": day,
            "high": random.randint(32, 40),
            "low": random.randint(22, 28),
            "irradiance": random.randint(600, 950)
        }
        for day in days
    ]
