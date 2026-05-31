"""
models.py — SQLAlchemy ORM table definitions
"""

from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class StatusEnum(str, enum.Enum):
    critical = "critical"
    moderate = "moderate"
    good     = "good"


class TrendEnum(str, enum.Enum):
    improving = "improving"
    declining = "declining"
    stable    = "stable"


class Lake(Base):
    __tablename__ = "lakes"

    id           = Column(Integer, primary_key=True, index=True)
    name         = Column(String(120), nullable=False, index=True)
    city         = Column(String(80))
    state        = Column(String(80))
    lat          = Column(Float, nullable=False)
    lng          = Column(Float, nullable=False)
    area_km2     = Column(Float)
    depth_m      = Column(Float)
    is_pilot     = Column(Boolean, default=False)
    status       = Column(String(20), default="moderate")
    trend        = Column(String(20), default="stable")
    health_score = Column(Integer, default=50)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())
    updated_at   = Column(DateTime(timezone=True), onupdate=func.now())

    sensor_readings = relationship("SensorReading", back_populates="lake", cascade="all, delete-orphan")
    reports         = relationship("CitizenReport",  back_populates="lake", cascade="all, delete-orphan")
    predictions     = relationship("Prediction",     back_populates="lake", cascade="all, delete-orphan")
    alerts          = relationship("Alert",          back_populates="lake", cascade="all, delete-orphan")


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id               = Column(Integer, primary_key=True, index=True)
    lake_id          = Column(Integer, ForeignKey("lakes.id"), nullable=False, index=True)
    timestamp        = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    do_mgl           = Column(Float)   # dissolved oxygen mg/L
    ph               = Column(Float)
    temp_c           = Column(Float)
    tds_ppm          = Column(Float)
    turbidity_ntu    = Column(Float)
    source           = Column(String(20), default="iot")   # iot | lab | imputed
    kalman_filtered  = Column(Boolean, default=False)
    raw_payload      = Column(Text)   # original MQTT JSON, for audit

    lake = relationship("Lake", back_populates="sensor_readings")


class CitizenReport(Base):
    __tablename__ = "citizen_reports"

    id         = Column(Integer, primary_key=True, index=True)
    lake_id    = Column(Integer, ForeignKey("lakes.id"), nullable=False, index=True)
    user_name  = Column(String(100))
    issue_type = Column(String(80))
    description= Column(Text)
    photo_url  = Column(String(500))
    lat        = Column(Float)
    lng        = Column(Float)
    status     = Column(String(30), default="Logged")
    ai_verified= Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    lake = relationship("Lake", back_populates="reports")


class Prediction(Base):
    __tablename__ = "predictions"

    id             = Column(Integer, primary_key=True, index=True)
    lake_id        = Column(Integer, ForeignKey("lakes.id"), nullable=False, index=True)
    generated_at   = Column(DateTime(timezone=True), server_default=func.now())
    horizon_days   = Column(Integer, default=7)
    model_version  = Column(String(30), default="lstm_v1")
    do_t7          = Column(Float)
    ph_t7          = Column(Float)
    temp_t7        = Column(Float)
    turbidity_t7   = Column(Float)
    chl_a_t7       = Column(Float)
    bloom_risk     = Column(Float)      # 0.0 – 1.0
    mosquito_risk  = Column(Float)      # 0.0 – 1.0
    confidence     = Column(Float)

    lake = relationship("Lake", back_populates="predictions")


class Alert(Base):
    __tablename__ = "alerts"

    id          = Column(Integer, primary_key=True, index=True)
    lake_id     = Column(String, ForeignKey("lakes.id"), nullable=False, index=True)

    severity    = Column(String)
    category    = Column(String)
    parameter   = Column(String)

    value       = Column(Float)
    threshold   = Column(Float)

    message     = Column(Text)
    action      = Column(Text)
    agency      = Column(Text)
    timeline    = Column(Text)

    is_resolved = Column(Boolean, default=False)

    created_at  = Column(DateTime)
    resolved_at = Column(DateTime)

    lake = relationship("Lake", back_populates="alerts")
