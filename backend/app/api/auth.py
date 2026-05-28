"""
routers/auth.py
POST /api/auth/token     — issue JWT (username + password)
POST /api/auth/api-key   — issue long-lived API key (for ESP32 nodes)
GET  /api/auth/me        — return current user from token

All protected endpoints import `require_auth` or `require_admin` from here.

Railway env vars required:
    SECRET_KEY   — random 32-byte hex string  (openssl rand -hex 32)
    ADMIN_USER   — admin username
    ADMIN_PASS   — admin password (hashed with bcrypt in production)
"""

import os
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, APIKeyHeader
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

router = APIRouter()

# ── Config ────────────────────────────────────────────────────────────────────

SECRET_KEY   = os.getenv("SECRET_KEY", "changeme-generate-with-openssl-rand-hex-32")
ALGORITHM    = "HS256"
TOKEN_EXPIRE = 60 * 24   # minutes — 24 hours

ADMIN_USER   = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS   = os.getenv("ADMIN_PASS", "lakepulse2025")   # override in Railway!

# Hardcoded ESP32 API keys: set as comma-separated in IOT_API_KEYS env var
# e.g.  IOT_API_KEYS=key_abc123,key_def456
IOT_API_KEYS = set(filter(None, os.getenv("IOT_API_KEYS", "dev-iot-key-1234").split(",")))

pwd_context   = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token", auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _create_token(data: dict, expires_minutes: int = TOKEN_EXPIRE) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=expires_minutes)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def _decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ── Dependencies — import these in other routers ──────────────────────────────

def require_auth(token: str = Depends(oauth2_scheme)):
    """Require a valid JWT. Returns the payload dict."""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return _decode_token(token)


def require_admin(payload: dict = Depends(require_auth)):
    """Require a JWT with role=admin."""
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return payload


def require_iot_key(api_key: str = Security(api_key_header)):
    """
    Lightweight check for ESP32 nodes — they send X-API-Key header.
    No DB lookup needed; keys are env-var configured per deployment.
    """
    if not api_key or api_key not in IOT_API_KEYS:
        raise HTTPException(status_code=403, detail="Invalid IoT API key")
    return api_key


# ── Schemas ───────────────────────────────────────────────────────────────────

class Token(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    role:         str
    expires_in:   int   # seconds


class UserOut(BaseModel):
    username: str
    role:     str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/token", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends()):
    """
    Standard OAuth2 password flow.
    In production: look up users from DB and verify bcrypt hash.
    For the hackathon: single admin account from env vars.
    """
    is_admin = (
        form.username == ADMIN_USER and
        form.password == ADMIN_PASS
    )
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    token = _create_token({"sub": form.username, "role": "admin"})
    return Token(
        access_token=token,
        role="admin",
        expires_in=TOKEN_EXPIRE * 60,
    )


@router.post("/api-key")
def issue_iot_api_key(payload: dict = Depends(require_admin)):
    """
    Generate a new random API key for an IoT node.
    In production: persist to DB and let admins revoke per-device.
    """
    key = "iot-" + secrets.token_hex(16)
    return {
        "api_key": key,
        "note": "Add this to IOT_API_KEYS in Railway env vars, then re-deploy.",
    }


@router.get("/me", response_model=UserOut)
def whoami(payload: dict = Depends(require_auth)):
    return UserOut(username=payload["sub"], role=payload.get("role", "viewer"))
