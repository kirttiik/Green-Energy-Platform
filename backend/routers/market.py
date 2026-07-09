from fastapi import APIRouter

router = APIRouter(
    prefix="/api/market",
    tags=["Market Intelligence"]
)

@router.get("/prices")
def get_market_prices():
    # Simulated data from real app.py extraction
    return {
        "dam_price": 4.15,
        "rtm_price": 4.85,
        "gtam_price": 5.20,
        "volume_traded": 1250.5,
        "clearing_price_trend": "+2.5%",
    }

@router.get("/chart")
def get_market_chart():
    # Simulated 24-hour DAM prices
    hours = [f"{i}:00" for i in range(24)]
    import random
    
    data = []
    for hour in range(24):
        # Higher prices during morning and evening peaks
        base = 3.5
        if 7 <= hour <= 10 or 17 <= hour <= 21:
            base = 5.5
        price = max(1.5, base + random.uniform(-1.0, 1.5))
        
        data.append({
            "hour": f"{hour}:00",
            "Price": round(price, 2),
            "Volume": random.randint(100, 500)
        })
        
    return data
