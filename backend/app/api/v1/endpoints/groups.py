from fastapi import APIRouter

from app.core.cache import get_cached, set_cached, delete_cached
from app.models.match import StandingRow
from app.services.football_api import fetch_group_standings

router = APIRouter(prefix="/groups", tags=["groups"])

_CACHE_KEY = "group_standings_v2"
_CACHE_TTL = 2 * 3600  # 2 hours — refresh frequently during the tournament


async def _build_and_cache() -> dict[str, list[StandingRow]]:
    standings = await fetch_group_standings()
    # Don't cache if all teams have 0 points — API probably failed and returned fallback zeros
    all_zero = all(row.mp == 0 for rows in standings.values() for row in rows)
    if not all_zero:
        await set_cached(
            _CACHE_KEY,
            {g: [r.model_dump() for r in rows] for g, rows in standings.items()},
            ttl=_CACHE_TTL,
        )
    return standings


@router.get("/standings", response_model=dict[str, list[StandingRow]])
async def group_standings():
    cached = await get_cached(_CACHE_KEY)
    if cached:
        return {g: [StandingRow(**r) for r in rows] for g, rows in cached.items()}
    return await _build_and_cache()


@router.post("/standings/refresh", response_model=dict[str, list[StandingRow]])
async def refresh_standings():
    await delete_cached(_CACHE_KEY)
    return await _build_and_cache()
