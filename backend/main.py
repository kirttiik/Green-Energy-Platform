from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from routers import executive, weather

app = FastAPI(
    title="Green Energy Platform API",
    description="Backend API for the Green Energy Platform Dashboard",
    version="1.0.0"
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with Vercel URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(executive.router)
app.include_router(weather.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Green Energy Platform API"}

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
