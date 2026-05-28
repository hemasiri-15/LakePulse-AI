"""
routers/reports.py  — citizen report submission + listing
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app import models

router = APIRouter()


class ReportCreate(BaseModel):
    lake_id:     int
    user_name:   str
    issue_type:  str
    description: str
    photo_url:   Optional[str] = None
    lat:         Optional[float] = None
    lng:         Optional[float] = None


class ReportOut(BaseModel):
    id:          int
    lake_id:     int
    user_name:   Optional[str]
    issue_type:  Optional[str]
    description: Optional[str]
    status:      str
    created_at:  datetime

    class Config:
        from_attributes = True


@router.post("", response_model=ReportOut, status_code=201)
def submit_report(data: ReportCreate, db: Session = Depends(get_db)):
    lake = db.query(models.Lake).filter(models.Lake.id == data.lake_id).first()
    if not lake:
        raise HTTPException(status_code=404, detail="Lake not found")
    report = models.CitizenReport(**data.dict())
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.get("", response_model=List[ReportOut])
def list_reports(lake_id: Optional[int] = None, limit: int = 50, db: Session = Depends(get_db)):
    q = db.query(models.CitizenReport).order_by(desc(models.CitizenReport.created_at))
    if lake_id:
        q = q.filter(models.CitizenReport.lake_id == lake_id)
    return q.limit(limit).all()


@router.put("/{report_id}/status")
def update_status(report_id: int, status: str, db: Session = Depends(get_db)):
    report = db.query(models.CitizenReport).filter(models.CitizenReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    allowed = {"Logged", "Under Review", "Escalated", "Action Taken", "Resolved"}
    if status not in allowed:
        raise HTTPException(status_code=400, detail=f"Status must be one of {allowed}")
    report.status = status
    db.commit()
    return {"id": report_id, "status": status}
