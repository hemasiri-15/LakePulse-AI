"""
routers/satellite.py
Stores and serves satellite-derived lake intelligence.
In production these records are written by a scheduled GEE script (see below).

GET  /api/satellite/{lake_id}/latest        — latest satellite event for a lake
GET  /api/satellite/{lake_id}/history       — time-series of NDWI / chl_a / area
GET  /api/satellite/{lake_id}/shrinkage     — % area lost since baseline year
POST /api/satellite/ingest                  — GEE script pushes results here
GET  /api/satellite/alerts                  — all events flagged as anomalies

─── Google Earth Engine script (run as Cloud Scheduler job) ──────────────────
The companion GEE script (gee_pipeline.js) computes NDWI, Chl-a, area change
and POSTs results to /api/satellite/ingest authenticated with an IoT API key.
See infra/gee_pipeline.js for the full implementation.
"""

from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import desc, Column, Integer, Float, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Session, relationship
from sqlalchemy.sql import func

from app.database import get_db, Base
from app.api.auth import require_iot_key, require_auth

router = APIRouter()


# ── ORM model (add to models.py import chain) ─────────────────────────────────
# Defined here for self-containment; in production move to models.py

class SatelliteEvent(Base):
    __tablename__ = "satellite_events"

    id            = Column(Integer, primary_key=True, index=True)
    lake_id       = Column(String, ForeignKey("lakes.id"), nullable=False, index=True)
    captured_date = Column(String(12), nullable=False)   # YYYY-MM-DD from GEE image date
    satellite     = Column(String(30), default="Sentinel-2")
    ndwi          = Column(Float)    # Normalised Difference Water Index  (−1 to +1)
    chl_a_ug_l    = Column(Float)    # Chlorophyll-a proxy  μg/L
    area_km2      = Column(Float)    # Water body area from NDWI threshold
    lst_celsius   = Column(Float)    # Land Surface Temperature anomaly
    is_anomaly    = Column(Boolean, default=False)
    anomaly_type  = Column(String(80))    # "bloom" | "shrinkage" | "thermal" | "encroachment"
    severity      = Column(String(20))    # critical | high | moderate | low
    notes         = Column(String(500))
    ingested_at   = Column(DateTime(timezone=True), server_default=func.now())


# ── Schemas ───────────────────────────────────────────────────────────────────

class SatelliteEventOut(BaseModel):
    id:            int
    lake_id:       str
    captured_date: str
    satellite:     str
    ndwi:          Optional[float]
    chl_a_ug_l:    Optional[float]
    area_km2:      Optional[float]
    lst_celsius:   Optional[float]
    is_anomaly:    bool
    anomaly_type:  Optional[str]
    severity:      Optional[str]
    notes:         Optional[str]
    ingested_at:   datetime

    class Config:
        from_attributes = True


class SatelliteIngest(BaseModel):
    lake_id:       str
    captured_date: str          # YYYY-MM-DD
    satellite:     str = "Sentinel-2"
    ndwi:          Optional[float] = None
    chl_a_ug_l:    Optional[float] = None
    area_km2:      Optional[float] = None
    lst_celsius:   Optional[float] = None
    notes:         Optional[str]  = None


class ShrinkageReport(BaseModel):
    lake_id:        str
    lake_name:      str
    baseline_date:  str
    baseline_km2:   float
    latest_date:    str
    latest_km2:     float
    change_pct:     float       # negative = shrinkage
    severity:       str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/{lake_id}/latest", response_model=SatelliteEventOut)
def latest_event(lake_id: str, db: Session = Depends(get_db)):
    event = (
        db.query(SatelliteEvent)
        .filter(SatelliteEvent.lake_id == lake_id)
        .order_by(desc(SatelliteEvent.captured_date))
        .first()
    )
    if not event:
        raise HTTPException(status_code=404, detail="No satellite data for this lake")
    return event


@router.get("/{lake_id}/history", response_model=List[SatelliteEventOut])
def event_history(
    lake_id: str,
    months:  int = 12,
    db:      Session = Depends(get_db),
):
    if months > 60:
        raise HTTPException(status_code=400, detail="Max 60 months")
    cutoff = (datetime.utcnow() - timedelta(days=months * 30)).strftime("%Y-%m-%d")
    events = (
        db.query(SatelliteEvent)
        .filter(
            SatelliteEvent.lake_id       == lake_id,
            SatelliteEvent.captured_date >= cutoff,
        )
        .order_by(SatelliteEvent.captured_date)
        .all()
    )
    return events


@router.get("/{lake_id}/shrinkage", response_model=ShrinkageReport)
def shrinkage_report(lake_id: str, db: Session = Depends(get_db)):
    """
    Returns % area change between the oldest and newest satellite record.
    A negative change_pct indicates lake shrinkage.
    """
    from app import models as m
    lake = db.query(m.Lake).filter(m.Lake.id == lake_id).first()
    if not lake:
        raise HTTPException(status_code=404, detail="Lake not found")

    oldest = (
        db.query(SatelliteEvent)
        .filter(SatelliteEvent.lake_id == lake_id, SatelliteEvent.area_km2.isnot(None))
        .order_by(SatelliteEvent.captured_date)
        .first()
    )
    newest = (
        db.query(SatelliteEvent)
        .filter(SatelliteEvent.lake_id == lake_id, SatelliteEvent.area_km2.isnot(None))
        .order_by(desc(SatelliteEvent.captured_date))
        .first()
    )

    if not oldest or not newest or oldest.id == newest.id:
        raise HTTPException(status_code=422, detail="Need at least 2 satellite records with area data")

    change_pct = ((newest.area_km2 - oldest.area_km2) / oldest.area_km2) * 100

    severity = (
        "critical" if change_pct < -20 else
        "high"     if change_pct < -10 else
        "moderate" if change_pct < -5  else
        "low"
    )

    return ShrinkageReport(
        lake_id       = lake_id,
        lake_name     = lake.name,
        baseline_date = oldest.captured_date,
        baseline_km2  = oldest.area_km2,
        latest_date   = newest.captured_date,
        latest_km2    = newest.area_km2,
        change_pct    = round(change_pct, 2),
        severity      = severity,
    )


@router.get("/alerts", response_model=List[SatelliteEventOut])
def satellite_anomalies(
    severity: Optional[str] = None,
    limit:    int = 50,
    db:       Session = Depends(get_db),
):
    q = (
        db.query(SatelliteEvent)
        .filter(SatelliteEvent.is_anomaly == True)
        .order_by(desc(SatelliteEvent.captured_date))
    )
    if severity:
        q = q.filter(SatelliteEvent.severity == severity)
    return q.limit(limit).all()


@router.post("/ingest", response_model=SatelliteEventOut, status_code=201)
def ingest_satellite(
    data:    SatelliteIngest,
    db:      Session = Depends(get_db),
    api_key: str = Depends(require_iot_key),   # GEE script uses same IoT key mechanism
):
    """
    Called by the scheduled GEE Python script.
    Auto-classifies anomalies based on threshold rules.
    """
    is_anomaly   = False
    anomaly_type = None
    severity     = None

    # Algal bloom: Chl-a > 50 μg/L is WHO threshold for high risk
    if data.chl_a_ug_l and data.chl_a_ug_l > 50:
        is_anomaly   = True
        anomaly_type = "bloom"
        severity     = "critical" if data.chl_a_ug_l > 100 else "high"

    # Thermal anomaly: LST > 2°C above seasonal average signals abnormal discharge
    elif data.lst_celsius and data.lst_celsius > 2.0:
        is_anomaly   = True
        anomaly_type = "thermal"
        severity     = "moderate"

    # NDWI < 0.2 with area data → possible shrinkage or encroachment
    elif data.ndwi is not None and data.ndwi < 0.2:
        is_anomaly   = True
        anomaly_type = "shrinkage"
        severity     = "high" if data.ndwi < 0.1 else "moderate"

    event = SatelliteEvent(
        lake_id       = data.lake_id,
        captured_date = data.captured_date,
        satellite     = data.satellite,
        ndwi          = data.ndwi,
        chl_a_ug_l    = data.chl_a_ug_l,
        area_km2      = data.area_km2,
        lst_celsius   = data.lst_celsius,
        is_anomaly    = is_anomaly,
        anomaly_type  = anomaly_type,
        severity      = severity,
        notes         = data.notes,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event
