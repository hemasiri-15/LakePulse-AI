"""
database.py — SQLAlchemy engine + session factory
Railway injects DATABASE_URL automatically when you add a Postgres plugin.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Railway sets DATABASE_URL; fall back to local SQLite for development
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./lakepulse_dev.db"
)
print("DATABASE_URL =", DATABASE_URL)

# Railway gives postgres:// but SQLAlchemy 1.4+ needs postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,       # auto-reconnect on stale connections
    pool_size=5,
    max_overflow=10,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
