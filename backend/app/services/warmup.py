import asyncio
import logging
from datetime import date, datetime, timezone

from app.core.budget import COST_PER_MATCH, DAILY_LIMIT_USD, is_over_limit, record_spend
from app.core.cache import get_cached, set_cached
from app.services.ai_service import get_prediction
from app.services.football_api import get_match_detail, get_upcoming_matches, refresh_scores_today, _load_scores_from_redis

logger = logging.getLogger("uvicorn.error")

_CONCURRENCY = 3
_FULL_TTL = 7 * 24 * 60 * 60   # 7 days for the full one-time load
_DAILY_TTL = 24 * 60 * 60       # 24 hours for daily-refreshed matches
_DAILY_INTERVAL = 24 * 60 * 60  # seconds between daily refreshes
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
        # Don't spend AI on finished matches — cache as-is for 7 days
        if detail.match.status == "finished":
            await set_cached(cache_key, detail.model_dump(), ttl=7 * 24 * 3600)
            logger.info("[warmup] fixture %d already finished, cached without AI", fixture_id)
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


_WARMUP_DAYS_AHEAD = 3   # only pre-compute matches happening within this many days


async def full_warmup() -> None:
    """Startup: pre-compute only uncached matches in the next _WARMUP_DAYS_AHEAD days.
    Matches further out are computed on-demand when a user visits the page.
    """
    from datetime import timedelta
    matches = await get_upcoming_matches()
    today = date.today()
    cutoff = (today + timedelta(days=_WARMUP_DAYS_AHEAD)).isoformat()
    today_str = today.isoformat()

    window = sorted(
        [m for m in matches if today_str <= m.kickoff_date <= cutoff],
        key=lambda m: m.kickoff_date,
    )

    uncached = []
    for m in window:
        c = await get_cached(f"match_detail_v4:{m.id}") or {}
        if not c.get("lineup") or not c.get("prediction_updated_at"):
            uncached.append(m)

    if not uncached:
        logger.info("[warmup] all %d matches in next %d days cached — skipping", len(window), _WARMUP_DAYS_AHEAD)
        return

    logger.info("[warmup] warming %d/%d uncached matches in next %d days", len(uncached), len(window), _WARMUP_DAYS_AHEAD)
    sem = asyncio.Semaphore(_CONCURRENCY)
    await asyncio.gather(*[
        _run_with_semaphore(m.id, _FULL_TTL, force=False, sem=sem)
        for m in uncached
    ])
    logger.info("[warmup] full warmup complete")


async def daily_refresh() -> None:
    """Refresh upcoming matches every 24 hours.

    Priority 1 — all matches in the next 48 hours (tomorrow's games must be fresh).
    Priority 2 — a few more from the broader schedule to warm the cache ahead of time.
    Skips any match whose prediction is newer than _FRESH_THRESHOLD_HOURS.
    """
    from datetime import timedelta
    today = date.today()
    tomorrow = (today + timedelta(days=2)).isoformat()
    today_str = today.isoformat()

    logger.info("[warmup] daily refresh for %s", today_str)
    matches = await get_upcoming_matches()
    sorted_matches = sorted(
        [m for m in matches if m.kickoff_date >= today_str],
        key=lambda m: m.kickoff_date,
    )

    # Priority: matches in the next 48h first, then the next 5 beyond that
    priority = [m for m in sorted_matches if m.kickoff_date <= tomorrow]
    extra = [m for m in sorted_matches if m.kickoff_date > tomorrow][:5]
    candidates = priority + extra

    if not candidates:
        logger.info("[warmup] no upcoming matches to refresh")
        return

    stale = []
    threshold = _FRESH_THRESHOLD_HOURS * 3600
    now = datetime.now(timezone.utc).timestamp()
    for m in candidates:
        cached = await get_cached(f"match_detail_v4:{m.id}") or {}
        updated_at = cached.get("prediction_updated_at")
        if updated_at:
            try:
                age = now - datetime.fromisoformat(updated_at).timestamp()
                if age < threshold:
                    logger.info("[warmup] fixture %d fresh (%.1fh old), skipping", m.id, age / 3600)
                    continue
            except Exception:
                pass
        stale.append(m)

    if not stale:
        logger.info("[warmup] all %d candidates have fresh predictions, nothing to do", len(candidates))
        return

    logger.info("[warmup] daily refresh: %d stale matches (%d priority + extra)", len(stale), len(priority))
    sem = asyncio.Semaphore(_CONCURRENCY)
    await asyncio.gather(*[
        _run_with_semaphore(m.id, _DAILY_TTL, force=True, sem=sem)
        for m in stale
    ])
    logger.info("[warmup] daily refresh complete (%d refreshed)", len(stale))


async def _scores_loop() -> None:
    """Refresh ESPN scores every 2 hours to pick up finished game results."""
    while True:
        await asyncio.sleep(7200)
        try:
            await refresh_scores_today()
        except Exception:
            pass


async def warm_cache() -> None:
    # Load finished scores from Redis before anything else — avoids ESPN re-fetch for old matches
    await _load_scores_from_redis()
    # Refresh scores from ESPN to pick up any new results
    await refresh_scores_today()
    # Run daily_refresh on startup to update stale predictions (skips any < 20h old).
    # This keeps predictions fresh across deploys without recomputing everything.
    await daily_refresh()
    asyncio.create_task(_scores_loop())
    while True:
        await asyncio.sleep(_DAILY_INTERVAL)
        await daily_refresh()
