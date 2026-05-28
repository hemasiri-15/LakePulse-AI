"""
routers/predictions.py + alerts.py
"""

# ── predictions.py ────────────────────────────────────────────────────────────
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app import models

router = APIRouter()


class PredictionOut(BaseModel):
    id:            int
    lake_id:       int
    generated_at:  datetime
    horizon_days:  int
    model_version: str
    do_t7:         Optional[float]
    ph_t7:         Optional[float]
    temp_t7:       Optional[float]
    turbidity_t7:  Optional[float]
    chl_a_t7:      Optional[float]
    bloom_risk:    Optional[float]
    mosquito_risk: Optional[float]
    confidence:    Optional[float]

    class Config:
        from_attributes = True


class PredictionCreate(BaseModel):
    lake_id:       int
    horizon_days:  int = 7
    model_version: str = "lstm_v1"
    do_t7:         Optional[float] = None
    ph_t7:         Optional[float] = None
    temp_t7:       Optional[float] = None
    turbidity_t7:  Optional[float] = None
    chl_a_t7:      Optional[float] = None
    bloom_risk:    Optional[float] = None
    mosquito_risk: Optional[float] = None
    confidence:    Optional[float] = None


@router.get("/{lake_id}/latest", response_model=PredictionOut)
def latest_prediction(lake_id: int, db: Session = Depends(get_db)):
    pred = (
        db.query(models.Prediction)
        .filter(models.Prediction.lake_id == lake_id)
        .order_by(desc(models.Prediction.generated_at))
        .first()
    )
    if not pred:
        raise HTTPException(status_code=404, detail="No predictions available")
    return pred


@router.post("", response_model=PredictionOut, status_code=201)
def store_prediction(data: PredictionCreate, db: Session = Depends(get_db)):
    """Called by the ML inference job after running the LSTM model."""
    pred = models.Prediction(**data.dict())
    db.add(pred)
    db.commit()
    db.refresh(pred)

    # Auto-generate alert if thresholds breached
    _check_and_alert(pred, db)
    return pred


def _check_and_alert(pred: models.Prediction, db: Session):
    alerts_to_create = []

    if pred.do_t7 is not None and pred.do_t7 < 3.0:
        alerts_to_create.append(models.Alert(
            lake_id    = pred.lake_id,
            alert_type = "Oxygen Depletion Risk",
            severity   = "critical" if pred.do_t7 < 2.0 else "high",
            message    = f"DO forecast: {pred.do_t7:.1f} mg/L in {pred.horizon_days} days (threshold: 3.0)",
        ))

    if pred.bloom_risk is not None and pred.bloom_risk > 0.75:
        alerts_to_create.append(models.Alert(
            lake_id    = pred.lake_id,
            alert_type = "Algal Bloom Risk",
            severity   = "critical" if pred.bloom_risk > 0.9 else "high",
            message    = f"Bloom probability: {pred.bloom_risk:.0%} in {pred.horizon_days} days",
        ))

    if pred.mosquito_risk is not None and pred.mosquito_risk > 0.8:
        alerts_to_create.append(models.Alert(
            lake_id    = pred.lake_id,
            alert_type = "Mosquito Outbreak Risk",
            severity   = "high",
            message    = f"Mosquito risk: {pred.mosquito_risk:.0%} in {pred.horizon_days} days",
        ))

    for alert in alerts_to_create:
        db.add(alert)
    if alerts_to_create:
        db.commit()


# ── alerts.py (imported separately in main.py) ────────────────────────────────
# This file intentionally combines both routers for brevity.
# In main.py, import alerts from this same module or split into separate files.

alerts_router = APIRouter()


class AlertOut(BaseModel):
    id:           int
    lake_id:      int
    alert_type:   Optional[str]
    severity:     Optional[str]
    message:      Optional[str]
    is_escalated: bool
    created_at:   datetime

    class Config:
        from_attributes = True


@alerts_router.get("", response_model=List[AlertOut])
def list_alerts(
    lake_id:  Optional[int] = None,
    severity: Optional[str] = None,
    limit:    int = 50,
    db:       Session = Depends(get_db),
):
    q = db.query(models.Alert).order_by(desc(models.Alert.created_at))
    if lake_id:
        q = q.filter(models.Alert.lake_id == lake_id)
    if severity:
        q = q.filter(models.Alert.severity == severity)
    return q.limit(limit).all()


@alerts_router.put("/{alert_id}/escalate")
def escalate_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.is_escalated = True
    db.commit()
    # In production: fire a webhook to GHMC here
    return {"id": alert_id, "escalated": True}
