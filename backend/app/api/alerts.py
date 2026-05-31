"""
routers/alerts.py
GET  /api/alerts              — list alerts (filter by lake, severity, resolved)
GET  /api/alerts/{id}         — single alert detail
PUT  /api/alerts/{id}/escalate  — mark escalated + fire GHMC webhook
PUT  /api/alerts/{id}/resolve   — mark resolved
POST /api/alerts/webhook/test   — test GHMC webhook (admin)
"""

import os
import httpx
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.cache import cache_set

router = APIRouter()

GHMC_WEBHOOK_URL = os.getenv("GHMC_WEBHOOK_URL", "")   # set in Railway env vars


# ── Schemas ───────────────────────────────────────────────────────────────────

class AlertOut(BaseModel):
    id: int
    lake_id: str

    severity: Optional[str]
    category: Optional[str]
    parameter: Optional[str]

    value: Optional[float]
    threshold: Optional[float]

    message: Optional[str]
    action: Optional[str]
    agency: Optional[str]
    timeline: Optional[str]

    is_resolved: bool

    created_at: datetime
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True

class AlertCreate(BaseModel):
    lake_id:    int
    alert_type: str
    severity:   str          # critical | high | moderate
    message:    str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("", response_model=List[AlertOut])
def list_alerts(
    lake_id:  Optional[str] = None,
    severity: Optional[str] = None,
    resolved: Optional[bool] = None,
    limit:    int = 50,
    db:       Session = Depends(get_db),
):
    q = db.query(models.Alert).order_by(desc(models.Alert.created_at))
    if lake_id is not None:
        q = q.filter(models.Alert.lake_id == lake_id)
    if severity:
        q = q.filter(models.Alert.severity == severity)
    if resolved is not None:
        q = q.filter(
            models.Alert.resolved_at.isnot(None) if resolved
            else models.Alert.resolved_at.is_(None)
        )
    return q.limit(limit).all()


@router.get("/{alert_id}", response_model=AlertOut)
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.post("", response_model=AlertOut, status_code=201)
def create_alert(data: AlertCreate, db: Session = Depends(get_db)):
    lake = db.query(models.Lake).filter(models.Lake.id == data.lake_id).first()
    if not lake:
        raise HTTPException(status_code=404, detail="Lake not found")
    alert = models.Alert(**data.dict())
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


@router.put("/{alert_id}/escalate")
def escalate_alert(
    alert_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    if alert.is_escalated:
        return {"id": alert_id, "escalated": True, "note": "already escalated"}

    alert.is_escalated = True
    db.commit()

    # Fire GHMC webhook in background so the response returns immediately
    lake = db.query(models.Lake).filter(models.Lake.id == alert.lake_id).first()
    background_tasks.add_task(
        _fire_ghmc_webhook,
        alert_id=alert_id,
        lake_name=lake.name if lake else "Unknown",
        alert_type=alert.alert_type,
        severity=alert.severity,
        message=alert.message,
    )
    return {"id": alert_id, "escalated": True}


@router.put("/{alert_id}/resolve")
def resolve_alert(
    alert_id:     int,
    action_taken: Optional[str] = None,
    db:           Session = Depends(get_db),
):
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.resolved_at  = datetime.utcnow()
    alert.action_taken = action_taken
    db.commit()
    return {"id": alert_id, "resolved": True}


@router.post("/webhook/test")
def test_webhook():
    """Fire a test payload to GHMC_WEBHOOK_URL to verify connectivity."""
    if not GHMC_WEBHOOK_URL:
        raise HTTPException(status_code=422, detail="GHMC_WEBHOOK_URL env var not set")
    payload = {
        "source":     "LakePulse AI",
        "test":       True,
        "alert_type": "System Test",
        "severity":   "low",
        "message":    "This is a test ping from LakePulse AI — webhook is configured correctly.",
    }
    try:
        resp = httpx.post(GHMC_WEBHOOK_URL, json=payload, timeout=8)
        return {"status": resp.status_code, "ok": resp.is_success}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Webhook call failed: {e}")


# ── Background helper ─────────────────────────────────────────────────────────

def _fire_ghmc_webhook(
    alert_id:   int,
    lake_name:  str,
    alert_type: str,
    severity:   str,
    message:    str,
):
    if not GHMC_WEBHOOK_URL:
        return   # silently skip if not configured

    payload = {
        "source":     "LakePulse AI",
        "alert_id":   alert_id,
        "lake":       lake_name,
        "alert_type": alert_type,
        "severity":   severity,
        "message":    message,
        "timestamp":  datetime.utcnow().isoformat(),
        "action_url": f"https://lakepulse.ai/alerts/{alert_id}",
    }
    try:
        httpx.post(GHMC_WEBHOOK_URL, json=payload, timeout=10)
    except Exception:
        pass   # log to Sentry in production; don't crash the background task
