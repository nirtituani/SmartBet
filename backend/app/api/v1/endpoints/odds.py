import json
import httpx
from fastapi import APIRouter

from app.core.cache import get_cached, set_cached
from app.services.football_api import _TEAM_META

router = APIRouter(prefix="/odds", tags=["odds"])

_POLYMARKET_URL = "https://gamma-api.polymarket.com/events/30615?_markets=true"
_CACHE_KEY = "wc_winner_odds_v1"
_CACHE_TTL = 3600

_NAME_MAP = {
    "United States": "USA",
    "Côte d'Ivoire": "Ivory Coast",
    "Cote d'Ivoire": "Ivory Coast",
    "Bosnia-Herzegovina": "Bosnia & Herzegovina",
    "Bosnia and Herzegovina": "Bosnia & Herzegovina",
    "Democratic Republic of Congo": "DR Congo",
    "Congo DR": "DR Congo",
}


@router.get("/wc-winner")
async def get_wc_winner_odds():
    cached = await get_cached(_CACHE_KEY)
    if cached:
        return cached

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(_POLYMARKET_URL)
        resp.raise_for_status()
        data = resp.json()

    markets = data.get("markets", [])
    result = []
    for market in markets:
        team_raw = (market.get("groupItemTitle") or "").strip()
        if not team_raw:
            continue

        prices = market.get("outcomePrices", [])
        if isinstance(prices, str):
            try:
                prices = json.loads(prices)
            except Exception:
                continue

        if not prices:
            continue

        try:
            prob = float(prices[0])
        except (ValueError, IndexError):
            continue

        if prob <= 0:
            continue

        team = _NAME_MAP.get(team_raw, team_raw)
        flag, _ = _TEAM_META.get(team, ("🏳️", 99))

        result.append({
            "team": team,
            "flag": flag,
            "probability": round(prob * 100, 2),
            "decimal_odds": round(1 / prob, 2),
        })

    result.sort(key=lambda x: -x["probability"])
    await set_cached(_CACHE_KEY, result, ttl=_CACHE_TTL)
    return result
