"""Daily spend tracker stored in Redis (falls back to in-memory)."""
from datetime import date

from app.core.cache import _redis

DAILY_LIMIT_USD = 1.00   # hard cap per day — change this to adjust
COST_PER_MATCH = 0.05    # conservative estimate per prediction + lineup call

_mem_spend: dict[str, float] = {}


def _today_key() -> str:
    return f"daily_spend:{date.today().isoformat()}"


async def get_spend() -> float:
    key = _today_key()
    if _redis is not None:
        try:
            val = await _redis.get(key)
            return float(val) if val else 0.0
        except Exception:
            pass
    return _mem_spend.get(key, 0.0)


async def record_spend(amount: float = COST_PER_MATCH) -> None:
    key = _today_key()
    if _redis is not None:
        try:
            await _redis.incrbyfloat(key, amount)
            await _redis.expire(key, 25 * 3600)  # auto-expire after 25h
            return
        except Exception:
            pass
    _mem_spend[key] = _mem_spend.get(key, 0.0) + amount


async def is_over_limit() -> bool:
    return await get_spend() >= DAILY_LIMIT_USD
