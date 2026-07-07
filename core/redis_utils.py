"""Centralized Redis access with short timeouts and safe fallbacks.

A single process-wide client is used so the connection pool is shared. Short
socket timeouts guarantee that a slow or unreachable Redis fails fast (raising
an exception we swallow) instead of blocking the request thread indefinitely
and, eventually, starving the whole worker pool.
"""

import logging

import redis
from django.conf import settings

logger = logging.getLogger("equiflow.redis")

_client = None

# Errors that mean "Redis is not answering right now". We treat all of them as
# a cache miss so the API degrades gracefully instead of hanging.
_REDIS_ERRORS = (redis.exceptions.RedisError, OSError)


def get_redis_client():
    """Return a lazily instantiated, shared Redis client with short timeouts."""
    global _client
    if _client is None:
        _client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_timeout=getattr(settings, "REDIS_SOCKET_TIMEOUT", 3),
            socket_connect_timeout=getattr(
                settings, "REDIS_SOCKET_CONNECT_TIMEOUT", 3
            ),
            retry_on_timeout=False,
            health_check_interval=30,
        )
    return _client


def safe_get(key, default=None):
    """GET that never raises: returns ``default`` on any Redis failure."""
    try:
        value = get_redis_client().get(key)
        return value if value is not None else default
    except _REDIS_ERRORS as exc:
        logger.warning("Redis GET failed for %r: %s", key, exc)
        return default


def safe_mget(keys):
    """MGET that never raises: returns a list of ``None`` on any failure."""
    keys = list(keys)
    if not keys:
        return []
    try:
        return get_redis_client().mget(keys)
    except _REDIS_ERRORS as exc:
        logger.warning("Redis MGET failed (%d keys): %s", len(keys), exc)
        return [None] * len(keys)


def _to_float(value, default):
    try:
        return float(value) if value not in (None, "") else default
    except (TypeError, ValueError):
        return default


def get_price(symbol):
    """Latest price for a single symbol, or ``None`` if unavailable."""
    return _to_float(safe_get(f"price_{symbol}"), None)


def get_change(symbol):
    """Latest 24h change for a single symbol, or ``0.0`` if unavailable."""
    return _to_float(safe_get(f"change_{symbol}"), 0.0)


def build_price_map(symbols):
    """Fetch prices AND changes for many symbols in a single MGET round trip.

    Returns ``{symbol: {"price": float|None, "change": float}}``. This is the
    fix for the N+1 pattern where each asset triggered its own Redis calls.
    """
    symbols = list(symbols)
    if not symbols:
        return {}

    price_keys = [f"price_{s}" for s in symbols]
    change_keys = [f"change_{s}" for s in symbols]
    values = safe_mget(price_keys + change_keys)

    mid = len(symbols)
    prices = values[:mid]
    changes = values[mid:]

    return {
        symbol: {
            "price": _to_float(price, None),
            "change": _to_float(change, 0.0),
        }
        for symbol, price, change in zip(symbols, prices, changes)
    }
