from fastapi import APIRouter
from pydantic import BaseModel
import datetime

router = APIRouter(
    prefix="/api/executive",
    tags=["Executive Dashboard"]
)

class ExecutiveOverview(BaseModel):
    today_forecast: float
    dam_price: float
    carbon_offset: float
    forecast_confidence: str
    weather_risk: str
    pipeline_health: str
    plant_health_score: int
    perf_ratio: float
    cap_factor: float
    latest_update: str

@router.get("/overview", response_model=ExecutiveOverview)
def get_executive_overview():
    # In Phase 2, we simulate the data extraction from app.py
    # Eventually, this will read from the actual data files like app.py does.
    
    # Static data extracted from app.py's render_executive_overview()
    return {
        "today_forecast": 12450.50,
        "dam_price": 4.15,
        "carbon_offset": 10209.4,
        "forecast_confidence": "High (96.4%)",
        "weather_risk": "Low",
        "pipeline_health": "🟢 100% Healthy",
        "plant_health_score": 92,
        "perf_ratio": 0.82,
        "cap_factor": 28.4,
        "latest_update": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    }

@router.get("/generation-chart")
def get_generation_chart_data():
    # Simulating hourly generation data for the chart
    hours = [f"{i}:00" for i in range(24)]
    
    data = []
    import random
    for hour in range(24):
        # Generate a bell curve-like shape for solar (daytime only)
        solar = 0
        if 6 <= hour <= 18:
            solar = max(0, 500 - (abs(12 - hour) * 80) + random.randint(-20, 20))
            
        # Wind is more variable
        wind = random.randint(100, 300)
        
        data.append({
            "hour": f"{hour}:00",
            "Solar": solar,
            "Wind": wind
        })
        
    return data
