from fastapi import APIRouter, HTTPException

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
    await set_cached("upcoming_matches", [m.model_dump() for m in matches], ttl=21600)
    return matches


@router.get("/{fixture_id}/predictions", response_model=MatchDetail)
async def match_predictions(fixture_id: int):
    cache_key = f"match_detail:{fixture_id}"
    cached = await get_cached(cache_key)
    if cached:
        return MatchDetail(**cached)

    detail = await get_match_detail(fixture_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="Match not found")

    detail.prediction = await get_prediction(
        detail.match, detail.home_form, detail.away_form, detail.h2h, detail.odds_comparison
    )
    await set_cached(cache_key, detail.model_dump(), ttl=21600)
    return detail
