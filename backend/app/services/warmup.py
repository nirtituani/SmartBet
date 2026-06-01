import asyncio
import logging

from app.core.cache import get_cached, set_cached
from app.services.ai_service import get_prediction
from app.services.football_api import get_match_detail, get_upcoming_matches

logger = logging.getLogger(__name__)

_MAX_WARM = 15        # warm the next N upcoming matches
_DELAY_SECS = 4       # pause between matches to avoid Claude rate limits


async def _warm_match(fixture_id: int) -> None:
    cache_key = f"match_detail_v2:{fixture_id}"
    cached = await get_cached(cache_key)
    if cached and "lineup" in cached:
        logger.info("[warmup] fixture %d already cached", fixture_id)
        return

    logger.info("[warmup] computing fixture %d", fixture_id)
    detail = await get_match_detail(fixture_id)
    if detail is None:
        logger.warning("[warmup] no detail returned for fixture %d", fixture_id)
        return

    detail.prediction = await get_prediction(
        detail.match, detail.home_form, detail.away_form, detail.h2h, detail.odds_comparison
    )
    await set_cached(cache_key, detail.model_dump(), ttl=43200)
    logger.info("[warmup] fixture %d done", fixture_id)


async def warm_cache() -> None:
    try:
        logger.info("[warmup] starting background cache warmup")
        matches = await get_upcoming_matches()
        to_warm = sorted(matches, key=lambda m: m.kickoff_date)[:_MAX_WARM]
        logger.info("[warmup] will warm %d matches", len(to_warm))
        for match in to_warm:
            try:
                await _warm_match(match.id)
            except Exception as exc:
                logger.error("[warmup] fixture %d error: %s", match.id, exc)
            await asyncio.sleep(_DELAY_SECS)
        logger.info("[warmup] all done")
    except Exception as exc:
        logger.error("[warmup] warmup task failed: %s", exc)
