"""
cache.py — Redis client with no-op fallback when Redis is unavailable.
Railway injects REDIS_URL when you add a Redis plugin.
"""

import os
import json
import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

_client = None

def get_cache_client():
    global _client
    if _client is None:
        _client = redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=2)
    return _client


def cache_get(key: str):
    try:
        val = get_cache_client().get(key)
        return json.loads(val) if val else None
    except Exception:
        return None


def cache_set(key: str, value, ttl_seconds: int = 30):
    try:
        get_cache_client().setex(key, ttl_seconds, json.dumps(value, default=str))
    except Exception:
        pass   # Redis unavailable — serve uncached


def cache_delete(key: str):
    try:
        get_cache_client().delete(key)
    except Exception:
        pass
