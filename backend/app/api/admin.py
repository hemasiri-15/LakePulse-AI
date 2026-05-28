"""
routers/admin.py
All endpoints require admin JWT (require_admin dependency).

GET  /api/admin/stats          — platform-wide counts + health summary
POST /api/admin/seed           — seed DB with the 12 reference lakes
POST /api/admin/seed/readings  — seed synthetic sensor readings (dev/demo)
DELETE /api/admin/lakes/{id}   — hard-delete a lake + cascade
POST /api/admin/score/all      — recompute health scores for every lake
"""

from datetime import datetime, timedelta
from typing import List
import random
import math

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.api.auth import require_admin
from app import models

router = APIRouter()

# ── Reference lake data (mirrors frontend LAKES constant) ─────────────────────
SEED_LAKES = [
    {"name":"Hussain Sagar",    "city":"Hyderabad",  "state":"Telangana",    "lat":17.424,"lng":78.474,"area_km2":5.7,   "depth_m":8.2,  "is_pilot":True},
    {"name":"Pragathi Nagar",   "city":"Hyderabad",  "state":"Telangana",    "lat":17.52, "lng":78.39, "area_km2":1.9,   "depth_m":3.1,  "is_pilot":True},
    {"name":"Bellandur Lake",   "city":"Bengaluru",  "state":"Karnataka",    "lat":12.921,"lng":77.67, "area_km2":3.6,   "depth_m":2.4,  "is_pilot":True},
    {"name":"Powai Lake",       "city":"Mumbai",     "state":"Maharashtra",  "lat":19.127,"lng":72.905,"area_km2":2.2,   "depth_m":12.4, "is_pilot":False},
    {"name":"Ulsoor Lake",      "city":"Bengaluru",  "state":"Karnataka",    "lat":12.982,"lng":77.619,"area_km2":1.2,   "depth_m":6.7,  "is_pilot":False},
    {"name":"Vembanad Lake",    "city":"Kochi",      "state":"Kerala",       "lat":9.6,   "lng":76.4,  "area_km2":2033,  "depth_m":11.8, "is_pilot":False},
    {"name":"Chilika Lake",     "city":"Puri",       "state":"Odisha",       "lat":19.7,  "lng":85.3,  "area_km2":1100,  "depth_m":4.2,  "is_pilot":False},
    {"name":"Sukhna Lake",      "city":"Chandigarh", "state":"Punjab",       "lat":30.742,"lng":76.818,"area_km2":3.0,   "depth_m":5.5,  "is_pilot":False},
    {"name":"Naini Lake",       "city":"Nainital",   "state":"Uttarakhand",  "lat":29.384,"lng":79.461,"area_km2":0.5,   "depth_m":27.3, "is_pilot":False},
    {"name":"Rankala Lake",     "city":"Kolhapur",   "state":"Maharashtra",  "lat":16.693,"lng":74.228,"area_km2":1.8,   "depth_m":4.1,  "is_pilot":False},
    {"name":"Loktak Lake",      "city":"Imphal",     "state":"Manipur",      "lat":24.5,  "lng":93.8,  "area_km2":287,   "depth_m":3.8,  "is_pilot":False},
    {"name":"Dal Lake",         "city":"Srinagar",   "state":"J&K",          "lat":34.09, "lng":74.85, "area_km2":18,    "depth_m":6.0,  "is_pilot":False},
]

# Realistic baseline parameters per lake
SEED_PARAMS = {
    "Hussain Sagar":  {"do":3.2,"ph":8.1,"temp":29,"tds":890,"turbidity":34},
    "Pragathi Nagar": {"do":1.8,"ph":8.6,"temp":31,"tds":1240,"turbidity":68},
    "Bellandur Lake": {"do":0.9,"ph":9.2,"temp":27,"tds":2100,"turbidity":92},
    "Powai Lake":     {"do":6.1,"ph":7.4,"temp":28,"tds":420,"turbidity":14},
    "Ulsoor Lake":    {"do":5.4,"ph":7.6,"temp":26,"tds":510,"turbidity":18},
    "Vembanad Lake":  {"do":7.2,"ph":7.1,"temp":27,"tds":310,"turbidity":8},
    "Chilika Lake":   {"do":7.8,"ph":7.2,"temp":26,"tds":280,"turbidity":6},
    "Sukhna Lake":    {"do":7.0,"ph":7.3,"temp":24,"tds":350,"turbidity":10},
    "Naini Lake":     {"do":7.5,"ph":7.0,"temp":18,"tds":290,"turbidity":9},
    "Rankala Lake":   {"do":4.8,"ph":7.7,"temp":27,"tds":680,"turbidity":22},
    "Loktak Lake":    {"do":5.8,"ph":7.2,"temp":22,"tds":380,"turbidity":12},
    "Dal Lake":       {"do":4.1,"ph":7.9,"temp":16,"tds":720,"turbidity":28},
}


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/stats")
def platform_stats(
    _: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    total_lakes    = db.query(func.count(models.Lake.id)).scalar()
    critical_lakes = db.query(func.count(models.Lake.id)).filter(models.Lake.status=="critical").scalar()
    total_readings = db.query(func.count(models.SensorReading.id)).scalar()
    total_reports  = db.query(func.count(models.CitizenReport.id)).scalar()
    open_alerts    = db.query(func.count(models.Alert.id)).filter(models.Alert.resolved_at.is_(None)).scalar()
    avg_score      = db.query(func.avg(models.Lake.health_score)).scalar()

    return {
        "lakes":          {"total": total_lakes, "critical": critical_lakes},
        "sensor_readings": total_readings,
        "citizen_reports": total_reports,
        "open_alerts":     open_alerts,
        "avg_health_score": round(float(avg_score or 0), 1),
        "generated_at":    datetime.utcnow().isoformat(),
    }


@router.post("/seed")
def seed_lakes(
    _: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Idempotent: skips lakes that already exist by name."""
    created = 0
    for data in SEED_LAKES:
        exists = db.query(models.Lake).filter(models.Lake.name == data["name"]).first()
        if not exists:
            lake = models.Lake(**data)
            db.add(lake)
            created += 1
    db.commit()
    return {"seeded": created, "skipped": len(SEED_LAKES) - created}


@router.post("/seed/readings")
def seed_readings(
    days: int = 30,
    _: dict = Depends(require_admin),
    db:  Session = Depends(get_db),
):
    """
    Generate synthetic 30-day sensor history for all lakes.
    Useful for demoing charts and the prediction tab before real ESP32 data arrives.
    """
    if days > 90:
        raise HTTPException(status_code=400, detail="Max 90 days")

    lakes   = db.query(models.Lake).all()
    created = 0
    rng     = random.Random(42)

    for lake in lakes:
        params = SEED_PARAMS.get(lake.name, {"do":5.0,"ph":7.5,"temp":26,"tds":500,"turbidity":15})
        for day_offset in range(days):
            ts = datetime.utcnow() - timedelta(days=days - day_offset)
            seasonal = math.sin(2 * math.pi * day_offset / 365)

            reading = models.SensorReading(
                lake_id        = lake.id,
                timestamp      = ts,
                do_mgl         = max(0.3, params["do"]        + seasonal * 0.8  + rng.gauss(0, 0.2)),
                ph             = params["ph"]                 + seasonal * 0.2  + rng.gauss(0, 0.05),
                temp_c         = params["temp"]               + seasonal * 2.0  + rng.gauss(0, 0.4),
                tds_ppm        = max(0, params["tds"]                           + rng.gauss(0, 30)),
                turbidity_ntu  = max(0, params["turbidity"]   + seasonal * 5.0  + rng.gauss(0, 3)),
                source         = "synthetic",
                kalman_filtered= True,
            )
            db.add(reading)
            created += 1

    db.commit()
    return {"readings_created": created, "lakes": len(lakes), "days": days}


@router.delete("/lakes/{lake_id}")
def delete_lake(
    lake_id: int,
    _: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    lake = db.query(models.Lake).filter(models.Lake.id == lake_id).first()
    if not lake:
        raise HTTPException(status_code=404, detail="Lake not found")
    db.delete(lake)
    db.commit()
    return {"deleted": lake_id}


@router.post("/score/all")
def recompute_all_scores(
    _: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Batch recompute health scores for every lake from its latest reading."""
    from sqlalchemy import desc as sqldesc
    lakes   = db.query(models.Lake).all()
    updated = 0

    for lake in lakes:
        latest = (
            db.query(models.SensorReading)
            .filter(models.SensorReading.lake_id == lake.id)
            .order_by(sqldesc(models.SensorReading.timestamp))
            .first()
        )
        if not latest:
            continue

        do_score   = min(100, max(0, (latest.do_mgl   / 9.0) * 100)) if latest.do_mgl   else 50
        ph_score   = max(0, 100 - abs(latest.ph - 7.0) * 20)          if latest.ph       else 50
        turb_score = min(100, max(0, 100 - latest.turbidity_ntu))      if latest.turbidity_ntu else 50
        tds_score  = min(100, max(0, 100 - (latest.tds_ppm / 20)))     if latest.tds_ppm  else 50

        score = int(0.25*do_score + 0.20*ph_score + 0.20*turb_score + 0.15*tds_score + 0.20*50)
        lake.health_score = score
        lake.status = "critical" if score < 40 else "moderate" if score < 65 else "good"
        updated += 1

    db.commit()
    return {"updated": updated}
