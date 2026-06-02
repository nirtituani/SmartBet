import asyncio
import logging
from datetime import date, timedelta

from app.core.cache import get_cached, set_cached
from app.services.ai_service import get_prediction
from app.services.football_api import get_match_detail, get_upcoming_matches

logger = logging.getLogger("uvicorn.error")

_CONCURRENCY = 3
_FULL_TTL = 7 * 24 * 60 * 60   # 7 days for the full one-time load
_DAILY_TTL = 24 * 60 * 60       # 24 hours for today's matches
_DAILY_INTERVAL = 24 * 60 * 60  # seconds between daily refreshes


async def _compute_match(fixture_id: int, ttl: int, force: bool = False) -> None:
    cache_key = f"match_detail_v2:{fixture_id}"
    if not force:
        cached = await get_cached(cache_key)
        if cached and "lineup" in cached:
            logger.info("[warmup] fixture %d already cached, skipping", fixture_id)
            return

    logger.info("[warmup] computing fixture %d", fixture_id)
    try:
        detail = await get_match_detail(fixture_id)
        if detail is None:
            logger.warning("[warmup] no detail for fixture %d", fixture_id)
            return
        detail.prediction = await get_prediction(
            detail.match, detail.home_form, detail.away_form, detail.h2h, detail.odds_comparison
        )
        await set_cached(cache_key, detail.model_dump(), ttl=ttl)
        logger.info("[warmup] fixture %d done", fixture_id)
    except Exception as exc:
        logger.error("[warmup] fixture %d error: %s", fixture_id, exc)


async def _run_with_semaphore(fixture_id: int, ttl: int, force: bool, sem: asyncio.Semaphore) -> None:
    async with sem:
        await _compute_match(fixture_id, ttl, force)


async def full_warmup() -> None:
    """One-time startup: warm all uncached matches with 7-day TTL."""
    logger.info("[warmup] full warmup starting")
    matches = await get_upcoming_matches()
    matches_sorted = sorted(matches, key=lambda m: m.kickoff_date)
    sem = asyncio.Semaphore(_CONCURRENCY)
    await asyncio.gather(*[
        _run_with_semaphore(m.id, _FULL_TTL, force=False, sem=sem)
        for m in matches_sorted
    ])
    logger.info("[warmup] full warmup complete (%d matches)", len(matches_sorted))


async def daily_refresh() -> None:
    """Refresh today's matches + all upcoming matches for teams that played yesterday."""
    today = date.today()
    yesterday = (today - timedelta(days=1)).isoformat()
    today_str = today.isoformat()
    logger.info("[warmup] daily refresh for %s", today_str)
    matches = await get_upcoming_matches()

    # Teams that played yesterday — their form changed
    recently_played = {
        name
        for m in matches if m.kickoff_date == yesterday
        for name in (m.home_team.name, m.away_team.name)
    }

    to_refresh = [
        m for m in matches
        if m.kickoff_date == today_str
        or m.home_team.name in recently_played
        or m.away_team.name in recently_played
    ]

    if not to_refresh:
        logger.info("[warmup] nothing to refresh today")
        return

    sem = asyncio.Semaphore(_CONCURRENCY)
    await asyncio.gather(*[
        _run_with_semaphore(m.id, _DAILY_TTL, force=True, sem=sem)
        for m in to_refresh
    ])
    logger.info("[warmup] daily refresh complete (%d matches)", len(to_refresh))


async def warm_cache() -> None:
    """Run full warmup once, then refresh next 6 every 24 hours."""
    await full_warmup()
    while True:
        await asyncio.sleep(_DAILY_INTERVAL)
        await daily_refresh()
