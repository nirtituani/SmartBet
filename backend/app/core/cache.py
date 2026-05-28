import json
import time
from typing import Any

from app.core.config import settings

_mem: dict[str, tuple[Any, float]] = {}

try:
    import redis.asyncio as aioredis
    _redis_available = True
except ImportError:
    _redis_available = False


async def get_cached(key: str) -> Any | None:
    if _redis_available:
        r = aioredis.from_url(settings.redis_url, decode_responses=True, socket_connect_timeout=1)
        try:
            val = await r.get(key)
            if val is not None:
                return json.loads(val)
        except Exception:
            pass
        finally:
            await r.aclose()
    entry = _mem.get(key)
    if entry and time.time() < entry[1]:
        return entry[0]
    _mem.pop(key, None)
    return None


async def set_cached(key: str, value: Any, ttl: int) -> None:
    if _redis_available:
        r = aioredis.from_url(settings.redis_url, decode_responses=True, socket_connect_timeout=1)
        try:
            await r.setex(key, ttl, json.dumps(value))
            return
        except Exception:
            pass
        finally:
            await r.aclose()
    _mem[key] = (value, time.time() + ttl)
