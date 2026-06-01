import asyncio
import logging

from app.core.cache import get_cached, set_cached
from app.services.ai_service import get_prediction
from app.services.football_api import get_match_detail, get_upcoming_matches

logger = logging.getLogger(__name__)

_CONCURRENCY = 3  # run 3 matches in parallel to stay within Claude rate limits


async def _warm_match(fixture_id: int, sem: asyncio.Semaphore) -> None:
    async with sem:
        cache_key = f"match_detail_v2:{fixture_id}"
        cached = await get_cached(cache_key)
        if cached and "lineup" in cached:
            logger.info("[warmup] fixture %d already cached", fixture_id)
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
            await set_cached(cache_key, detail.model_dump(), ttl=43200)
            logger.info("[warmup] fixture %d done", fixture_id)
        except Exception as exc:
            logger.error("[warmup] fixture %d error: %s", fixture_id, exc)


async def warm_cache() -> None:
    try:
        logger.info("[warmup] starting")
        matches = await get_upcoming_matches()
        matches_sorted = sorted(matches, key=lambda m: m.kickoff_date)
        logger.info("[warmup] warming all %d matches", len(matches_sorted))
        sem = asyncio.Semaphore(_CONCURRENCY)
        await asyncio.gather(*[_warm_match(m.id, sem) for m in matches_sorted])
        logger.info("[warmup] complete")
    except Exception as exc:
        logger.error("[warmup] failed: %s", exc)
