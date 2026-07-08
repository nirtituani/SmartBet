from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.core.budget import COST_PER_MATCH, is_over_limit, record_spend
from app.core.cache import get_cached, set_cached
from app.models.match import Match, MatchDetail
from app.services.ai_service import get_prediction
from app.services.football_api import get_match_detail, get_upcoming_matches, fetch_espn_lineup

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
    cache_key = f"match_detail_v5:{fixture_id}"
    cached = await get_cached(cache_key)

    if cached and 'lineup' in cached:
        detail = MatchDetail(**cached)
        # If lineup is still predicted and match is within 3 hours, try to get real lineup
        lineup_is_predicted = cached.get("lineup", {}).get("is_predicted", True) if cached.get("lineup") else True
        if lineup_is_predicted:
            try:
                kickoff = datetime.fromisoformat(f"{detail.match.kickoff_date}T{detail.match.kickoff_time}:00+03:00")
                mins_to_kickoff = (kickoff - datetime.now(timezone.utc)).total_seconds() / 60
                if -60 <= mins_to_kickoff <= 180:  # between 3h before and 1h after kickoff
                    real_lineup = await fetch_espn_lineup(
                        detail.match.home_team.name, detail.match.away_team.name, detail.match.kickoff_date
                    )
                    if real_lineup:
                        detail.lineup = real_lineup
                        updated = cached.copy()
                        updated["lineup"] = real_lineup.model_dump()
                        await set_cached(cache_key, updated, ttl=43200)
            except Exception:
                pass
        return detail

    detail = await get_match_detail(fixture_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="Match not found")

    # Finished match: preserve any pre-match prediction that was already cached
    if detail.match.status == "finished":
        existing = await get_cached(cache_key)
        if existing and existing.get("prediction"):
            existing["match"] = detail.match.model_dump()
            await set_cached(cache_key, existing, ttl=7 * 24 * 3600)
            return MatchDetail(**existing)
        await set_cached(cache_key, detail.model_dump(), ttl=7 * 24 * 3600)
        return detail

    if not await is_over_limit():
        detail.prediction = await get_prediction(
            detail.match, detail.home_form, detail.away_form, detail.h2h, detail.odds_comparison
        )
        detail.prediction_updated_at = datetime.now(timezone.utc).isoformat()
        await record_spend(COST_PER_MATCH)
        await set_cached(cache_key, detail.model_dump(), ttl=43200)  # 12h — refresh twice a day
    else:
        # Don't cache when prediction is skipped — retry on next request once limit resets
        pass

    return detail
