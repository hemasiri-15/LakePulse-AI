"""
LakePulse AI — FastAPI Backend
================================
Deploy to Railway:  railway up
Local dev:          uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn, os

from app.database import engine
from app.models import Base
from app.api import lakes, sensors, reports, predictions
from app.api.alerts import router as alerts_router
from app.api.auth import router as auth_router
from app.api.admin import router as admin_router
from app.api.satellite import router as satellite_router
from app.cache import get_cache_client

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LakePulse AI",
    description="National Smart Lake Monitoring — REST API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

from app.database import DATABASE_URL

@app.get("/debug-db")
def debug_db():
    return {"database_url": DATABASE_URL[:50]}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten to Vercel URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router,      prefix="/api/auth",        tags=["Auth"])
app.include_router(lakes.router,     prefix="/api/lakes",       tags=["Lakes"])
app.include_router(sensors.router,   prefix="/api/sensors",     tags=["Sensors"])
app.include_router(reports.router,   prefix="/api/reports",     tags=["Reports"])
app.include_router(predictions.router,prefix="/api/predictions",tags=["Predictions"])
app.include_router(alerts_router,    prefix="/api/alerts",      tags=["Alerts"])
app.include_router(satellite_router, prefix="/api/satellite",   tags=["Satellite"])
app.include_router(admin_router,     prefix="/api/admin",       tags=["Admin"])

@app.get("/health", tags=["System"])
async def health():
    try:
        get_cache_client().ping()
        redis_ok = True
    except Exception:
        redis_ok = False
    return {"status": "ok", "version": "1.0.0",
            "redis": "ok" if redis_ok else "unavailable", "database": "ok"}

@app.get("/", tags=["System"])
async def root():
    return {"message": "LakePulse AI API — visit /docs for the full API reference"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=False)
