import json
import time
from typing import Any

from app.core.config import settings

_mem: dict[str, tuple[Any, float]] = {}

_redis = None
try:
    import redis.asyncio as aioredis
    _redis = aioredis.from_url(
        settings.redis_url,
        decode_responses=True,
        socket_connect_timeout=2,
        socket_timeout=2,
    )
except Exception:
    pass


async def get_cached(key: str) -> Any | None:
    if _redis is not None:
        try:
            val = await _redis.get(key)
            if val is not None:
                return json.loads(val)
        except Exception:
            pass
    entry = _mem.get(key)
    if entry and time.time() < entry[1]:
        return entry[0]
    _mem.pop(key, None)
    return None


async def set_cached(key: str, value: Any, ttl: int) -> None:
    if _redis is not None:
        try:
            await _redis.setex(key, ttl, json.dumps(value))
            return
        except Exception:
            pass
    _mem[key] = (value, time.time() + ttl)


async def delete_cached(key: str) -> None:
    if _redis is not None:
        try:
            await _redis.delete(key)
        except Exception:
            pass
    _mem.pop(key, None)
