from fastapi import APIRouter

from app.core.cache import get_cached, set_cached, delete_cached
from app.models.match import StandingRow
from app.services.football_api import _fetch_wc_results, calculate_group_standings

router = APIRouter(prefix="/groups", tags=["groups"])

_CACHE_KEY = "group_standings"
_CACHE_TTL = 7 * 24 * 3600  # keep until manually refreshed (1 week fallback)


async def _build_and_cache() -> dict[str, list[StandingRow]]:
    results = await _fetch_wc_results()
    standings = calculate_group_standings(results)
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
