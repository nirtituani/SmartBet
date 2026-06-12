from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.core.budget import COST_PER_MATCH, is_over_limit, record_spend
from app.core.cache import get_cached, set_cached
from app.models.match import Match, MatchDetail
from app.services.ai_service import get_prediction
from app.services.football_api import get_match_detail, get_upcoming_matches

router = APIRouter(prefix="/matches", tags=["matches"])


@router.get("/upcoming", response_model=list[Match])
async def upcoming_matches():
    cached = await get_cached("upcoming_matches")
    if cached:
        return [Match(**m) for m in cached]
    matches = await get_upcoming_matches()
    # Cache real data for 6 hours; mock data for 2 minutes so the real API is retried soon
    is_mock = matches and matches[0].kickoff_date.startswith("2026-07")
    ttl = 120 if is_mock else 21600
    await set_cached("upcoming_matches", [m.model_dump() for m in matches], ttl=ttl)
    return matches


@router.get("/{fixture_id}/predictions", response_model=MatchDetail)
async def match_predictions(fixture_id: int):
    cache_key = f"match_detail_v4:{fixture_id}"
    cached = await get_cached(cache_key)
    if cached and 'lineup' in cached:
        return MatchDetail(**cached)

    detail = await get_match_detail(fixture_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="Match not found")

    if await is_over_limit():
        raise HTTPException(status_code=503, detail="Daily AI budget reached, try again tomorrow")

    detail.prediction = await get_prediction(
        detail.match, detail.home_form, detail.away_form, detail.h2h, detail.odds_comparison
    )
    detail.prediction_updated_at = datetime.now(timezone.utc).isoformat()
    await record_spend(COST_PER_MATCH)
    await set_cached(cache_key, detail.model_dump(), ttl=43200)  # 12h — refresh twice a day
    return detail
