import json
import time
from typing import Any

from app.core.config import settings

_mem: dict[str, tuple[Any, float]] = {}


async def get_cached(key: str) -> Any | None:
    try:
        import redis.asyncio as aioredis
        r = aioredis.from_url(settings.redis_url, decode_responses=True, socket_connect_timeout=1)
        val = await r.get(key)
        await r.aclose()
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
    try:
        import redis.asyncio as aioredis
        r = aioredis.from_url(settings.redis_url, decode_responses=True, socket_connect_timeout=1)
        await r.setex(key, ttl, json.dumps(value))
        await r.aclose()
        return
    except Exception:
        pass
    _mem[key] = (value, time.time() + ttl)
