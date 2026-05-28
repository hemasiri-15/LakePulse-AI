"""
routers/lakes.py
GET  /api/lakes          — list all lakes (cached 30s)
GET  /api/lakes/{id}     — single lake with latest reading
POST /api/lakes          — create lake (admin)
PUT  /api/lakes/{id}/score — recalculate health score
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from pydantic import BaseModel
from app.database import get_db
from app import models
from app.cache import cache_get, cache_set

router = APIRouter()


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class LakeOut(BaseModel):
    id:           int
    name:         str
    city:         Optional[str]
    state:        Optional[str]
    lat:          float
    lng:          float
    area_km2:     Optional[float]
    depth_m:      Optional[float]
    is_pilot:     bool
    status:       str
    trend:        str
    health_score: int

    class Config:
        from_attributes = True


class LakeCreate(BaseModel):
    name:     str
    city:     Optional[str]
    state:    Optional[str]
    lat:      float
    lng:      float
    area_km2: Optional[float]
    depth_m:  Optional[float]
    is_pilot: bool = False


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("", response_model=List[LakeOut])
def list_lakes(db: Session = Depends(get_db)):
    cached = cache_get("lakes:all")
    if cached:
        return cached

    lakes = db.query(models.Lake).order_by(models.Lake.health_score).all()
    result = [LakeOut.from_orm(l).dict() for l in lakes]
    cache_set("lakes:all", result, ttl_seconds=30)
    return result


@router.get("/{lake_id}", response_model=LakeOut)
def get_lake(lake_id: int, db: Session = Depends(get_db)):
    lake = db.query(models.Lake).filter(models.Lake.id == lake_id).first()
    if not lake:
        raise HTTPException(status_code=404, detail="Lake not found")
    return lake


@router.post("", response_model=LakeOut, status_code=201)
def create_lake(data: LakeCreate, db: Session = Depends(get_db)):
    lake = models.Lake(**data.dict())
    db.add(lake)
    db.commit()
    db.refresh(lake)
    cache_set("lakes:all", None)   # invalidate list cache
    return lake


@router.put("/{lake_id}/score")
def recalculate_score(lake_id: int, db: Session = Depends(get_db)):
    """
    Recomputes composite health score from the latest sensor reading.
    Weights: DO=25, pH=20, turbidity=20, TDS=15, WQI=20
    """
    lake = db.query(models.Lake).filter(models.Lake.id == lake_id).first()
    if not lake:
        raise HTTPException(status_code=404, detail="Lake not found")

    latest = (
        db.query(models.SensorReading)
        .filter(models.SensorReading.lake_id == lake_id)
        .order_by(desc(models.SensorReading.timestamp))
        .first()
    )
    if not latest:
        raise HTTPException(status_code=422, detail="No sensor readings for this lake")

    # Normalised sub-scores (0–100)
    do_score  = min(100, max(0, (latest.do_mgl  / 9.0)  * 100)) if latest.do_mgl  else 50
    ph_score  = max(0, 100 - abs(latest.ph - 7.0) * 20)          if latest.ph      else 50
    turb_score= min(100, max(0, 100 - latest.turbidity_ntu))      if latest.turbidity_ntu else 50
    tds_score = min(100, max(0, 100 - (latest.tds_ppm / 20)))     if latest.tds_ppm else 50

    composite = (
        0.25 * do_score +
        0.20 * ph_score +
        0.20 * turb_score +
        0.15 * tds_score +
        0.20 * 50          # placeholder for biodiversity — update when available
    )
    score = int(round(composite))

    lake.health_score = score
    lake.status = "critical" if score < 40 else "moderate" if score < 65 else "good"
    db.commit()

    cache_set("lakes:all", None)
    return {"lake_id": lake_id, "health_score": score, "status": lake.status}
