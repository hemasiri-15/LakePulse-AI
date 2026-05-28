"""
routers/sensors.py
POST /api/sensors/ingest        — ESP32 pushes readings here (MQTT bridge or direct HTTP)
GET  /api/sensors/{lake_id}/latest  — latest reading for a lake
GET  /api/sensors/{lake_id}/history — last N days of readings
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, timedelta
import json

from app.database import get_db
from app import models
from app.cache import cache_set, cache_get

router = APIRouter()


# ── Kalman filter (1-D per parameter) ────────────────────────────────────────

class KalmanFilter1D:
    """Lightweight scalar Kalman filter for sensor noise reduction."""
    def __init__(self, process_noise=1e-3, measurement_noise=0.1):
        self.Q  = process_noise
        self.R  = measurement_noise
        self.x  = None   # state estimate
        self.P  = 1.0    # estimate covariance

    def update(self, measurement: float) -> float:
        if self.x is None:
            self.x = measurement
            return measurement
        # Predict
        P_pred = self.P + self.Q
        # Update
        K      = P_pred / (P_pred + self.R)
        self.x = self.x + K * (measurement - self.x)
        self.P = (1 - K) * P_pred
        return self.x

# One filter instance per (lake_id, parameter) — lives in memory between requests
_filters: dict = {}

def get_filter(lake_id: int, param: str) -> KalmanFilter1D:
    key = f"{lake_id}:{param}"
    if key not in _filters:
        _filters[key] = KalmanFilter1D()
    return _filters[key]


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class SensorIngest(BaseModel):
    lake_id:       int
    do_mgl:        Optional[float] = None
    ph:            Optional[float] = None
    temp_c:        Optional[float] = None
    tds_ppm:       Optional[float] = None
    turbidity_ntu: Optional[float] = None
    source:        str = "iot"
    raw_payload:   Optional[str] = None   # pass the raw MQTT JSON string for audit

class ReadingOut(BaseModel):
    id:            int
    lake_id:       int
    timestamp:     datetime
    do_mgl:        Optional[float]
    ph:            Optional[float]
    temp_c:        Optional[float]
    tds_ppm:       Optional[float]
    turbidity_ntu: Optional[float]
    source:        str
    kalman_filtered: bool

    class Config:
        from_attributes = True


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/ingest", response_model=ReadingOut, status_code=201)
def ingest_reading(
    data: SensorIngest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Called by the ESP32 (via MQTT-HTTP bridge) or directly over WiFi.
    Applies per-lake Kalman filtering before storing.
    """
    lake = db.query(models.Lake).filter(models.Lake.id == data.lake_id).first()
    if not lake:
        raise HTTPException(status_code=404, detail=f"Lake {data.lake_id} not found")

    # Apply Kalman filter to each parameter
    filtered = {}
    for param in ["do_mgl", "ph", "temp_c", "tds_ppm", "turbidity_ntu"]:
        raw = getattr(data, param)
        if raw is not None:
            filtered[param] = round(get_filter(data.lake_id, param).update(raw), 4)
        else:
            filtered[param] = None

    reading = models.SensorReading(
        lake_id         = data.lake_id,
        do_mgl          = filtered["do_mgl"],
        ph              = filtered["ph"],
        temp_c          = filtered["temp_c"],
        tds_ppm         = filtered["tds_ppm"],
        turbidity_ntu   = filtered["turbidity_ntu"],
        source          = data.source,
        kalman_filtered = True,
        raw_payload     = data.raw_payload,
    )
    db.add(reading)
    db.commit()
    db.refresh(reading)

    # Bust the latest-reading cache for this lake
    cache_set(f"sensor:latest:{data.lake_id}", None)

    # Recalculate health score in background (non-blocking)
    background_tasks.add_task(_update_lake_score, data.lake_id, db)

    return reading


@router.get("/{lake_id}/latest", response_model=ReadingOut)
def latest_reading(lake_id: int, db: Session = Depends(get_db)):
    cached = cache_get(f"sensor:latest:{lake_id}")
    if cached:
        return cached

    reading = (
        db.query(models.SensorReading)
        .filter(models.SensorReading.lake_id == lake_id)
        .order_by(desc(models.SensorReading.timestamp))
        .first()
    )
    if not reading:
        raise HTTPException(status_code=404, detail="No readings found for this lake")

    result = ReadingOut.from_orm(reading).dict()
    cache_set(f"sensor:latest:{lake_id}", result, ttl_seconds=30)
    return result


@router.get("/{lake_id}/history", response_model=List[ReadingOut])
def reading_history(
    lake_id: int,
    days: int = 7,
    db: Session = Depends(get_db),
):
    if days > 90:
        raise HTTPException(status_code=400, detail="Max 90 days")
    cutoff = datetime.utcnow() - timedelta(days=days)
    readings = (
        db.query(models.SensorReading)
        .filter(
            models.SensorReading.lake_id  == lake_id,
            models.SensorReading.timestamp >= cutoff,
        )
        .order_by(models.SensorReading.timestamp)
        .all()
    )
    return readings


# ── Background task ───────────────────────────────────────────────────────────

def _update_lake_score(lake_id: int, db: Session):
    """Recompute composite health score after every new reading."""
    lake = db.query(models.Lake).filter(models.Lake.id == lake_id).first()
    if not lake:
        return
    latest = (
        db.query(models.SensorReading)
        .filter(models.SensorReading.lake_id == lake_id)
        .order_by(desc(models.SensorReading.timestamp))
        .first()
    )
    if not latest:
        return

    do_score   = min(100, max(0, (latest.do_mgl   / 9.0) * 100)) if latest.do_mgl   else 50
    ph_score   = max(0, 100 - abs(latest.ph - 7.0) * 20)          if latest.ph       else 50
    turb_score = min(100, max(0, 100 - latest.turbidity_ntu))      if latest.turbidity_ntu else 50
    tds_score  = min(100, max(0, 100 - (latest.tds_ppm / 20)))     if latest.tds_ppm  else 50

    score = int(0.25*do_score + 0.20*ph_score + 0.20*turb_score + 0.15*tds_score + 0.20*50)
    lake.health_score = score
    lake.status = "critical" if score < 40 else "moderate" if score < 65 else "good"
    db.commit()
