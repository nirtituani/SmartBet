import asyncio
import logging
from datetime import date, datetime, timezone

from app.core.budget import COST_PER_MATCH, DAILY_LIMIT_USD, is_over_limit, record_spend
from app.core.cache import get_cached, set_cached
from app.services.ai_service import get_prediction
from app.services.football_api import get_match_detail, get_upcoming_matches, refresh_scores_today

logger = logging.getLogger("uvicorn.error")

_CONCURRENCY = 3
_FULL_TTL = 7 * 24 * 60 * 60   # 7 days for the full one-time load
_DAILY_TTL = 24 * 60 * 60       # 24 hours for daily-refreshed matches
_DAILY_INTERVAL = 24 * 60 * 60  # seconds between daily refreshes
_DAILY_REFRESH_COUNT = 3        # only refresh the next N upcoming matches
_FRESH_THRESHOLD_HOURS = 20     # skip daily refresh if prediction is newer than this


async def _compute_match(fixture_id: int, ttl: int, force: bool = False) -> None:
    if await is_over_limit():
        logger.warning("[warmup] daily limit $%.2f reached, skipping fixture %d", DAILY_LIMIT_USD, fixture_id)
        return

    cache_key = f"match_detail_v4:{fixture_id}"
    if not force:
        cached = await get_cached(cache_key)
        if cached and cached.get("lineup") and cached.get("prediction_updated_at"):
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
        detail.prediction_updated_at = datetime.now(timezone.utc).isoformat()
        await set_cached(cache_key, detail.model_dump(), ttl=ttl)
        await record_spend(COST_PER_MATCH)
        logger.info("[warmup] fixture %d done (estimated spend today: $%.2f)", fixture_id, await _get_spend_safe())
    except Exception as exc:
        logger.error("[warmup] fixture %d error: %s", fixture_id, exc)


async def _get_spend_safe() -> float:
    from app.core.budget import get_spend
    try:
        return await get_spend()
    except Exception:
        return 0.0


async def _run_with_semaphore(fixture_id: int, ttl: int, force: bool, sem: asyncio.Semaphore) -> None:
    async with sem:
        await _compute_match(fixture_id, ttl, force)


async def full_warmup() -> None:
    """Startup: warm only uncached upcoming matches. Never spends AI on finished games."""
    matches = await get_upcoming_matches()
    today = date.today().isoformat()
    matches_sorted = sorted(
        [m for m in matches if m.kickoff_date >= today],
        key=lambda m: m.kickoff_date,
    )

    needs_compute = []
    for m in matches_sorted:
        c = await get_cached(f"match_detail_v4:{m.id}") or {}
        if not c.get("lineup") or not c.get("prediction_updated_at"):
            needs_compute.append(m)
    uncached = needs_compute

    if not uncached:
        logger.info("[warmup] all %d matches cached — skipping full warmup", len(matches_sorted))
        return

    logger.info("[warmup] full warmup: %d/%d matches need computing (daily limit: $%.2f)",
                len(uncached), len(matches_sorted), DAILY_LIMIT_USD)
    sem = asyncio.Semaphore(_CONCURRENCY)
    await asyncio.gather(*[
        _run_with_semaphore(m.id, _FULL_TTL, force=False, sem=sem)
        for m in uncached
    ])
    logger.info("[warmup] full warmup complete")


async def daily_refresh() -> None:
    """Refresh the next N upcoming matches every 24 hours, skipping fresh ones."""
    today = date.today().isoformat()
    logger.info("[warmup] daily refresh for %s", today)
    matches = await get_upcoming_matches()
    next_n = sorted(
        [m for m in matches if m.kickoff_date >= today],
        key=lambda m: m.kickoff_date
    )[:_DAILY_REFRESH_COUNT]
    if not next_n:
        logger.info("[warmup] no upcoming matches to refresh")
        return

    stale = []
    threshold = _FRESH_THRESHOLD_HOURS * 3600
    now = datetime.now(timezone.utc).timestamp()
    for m in next_n:
        cached = await get_cached(f"match_detail_v4:{m.id}") or {}
        updated_at = cached.get("prediction_updated_at")
        if updated_at:
            try:
                age = now - datetime.fromisoformat(updated_at).timestamp()
                if age < threshold:
                    logger.info("[warmup] fixture %d prediction is fresh (%.1fh old), skipping", m.id, age / 3600)
                    continue
            except Exception:
                pass
        stale.append(m)

    if not stale:
        logger.info("[warmup] all %d matches have fresh predictions, skipping daily refresh", len(next_n))
        return

    sem = asyncio.Semaphore(_CONCURRENCY)
    await asyncio.gather(*[
        _run_with_semaphore(m.id, _DAILY_TTL, force=True, sem=sem)
        for m in stale
    ])
    logger.info("[warmup] daily refresh complete (%d/%d matches refreshed)", len(stale), len(next_n))


async def _scores_loop() -> None:
    """Refresh ESPN scores every 2 hours to pick up finished game results."""
    while True:
        await asyncio.sleep(7200)
        try:
            await refresh_scores_today()
        except Exception:
            pass


async def warm_cache() -> None:
    await refresh_scores_today()
    await full_warmup()
    asyncio.create_task(_scores_loop())
    while True:
        await asyncio.sleep(_DAILY_INTERVAL)
        await daily_refresh()
