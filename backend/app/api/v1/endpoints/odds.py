import json
import httpx
from fastapi import APIRouter

from app.core.cache import get_cached, set_cached
from app.core.config import settings
from app.services.football_api import _TEAM_META

router = APIRouter(prefix="/odds", tags=["odds"])

_POLYMARKET_URL = "https://gamma-api.polymarket.com/events/30615?_markets=true"
_ODDS_API_URL = "https://api.the-odds-api.com/v4/sports/soccer_fifa_world_cup_winner/odds/"

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
    cached = await get_cached("wc_winner_odds_v1")
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
    await set_cached("wc_winner_odds_v1", result, ttl=3600)
    return result


@router.get("/wc-winner-bookmakers")
async def get_wc_winner_bookmakers():
    cached = await get_cached("wc_winner_bookmakers_v1")
    if cached:
        return cached

    params = {
        "apiKey": settings.odds_api_key,
        "markets": "outrights",
        "regions": "eu,uk",
        "oddsFormat": "decimal",
    }

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(_ODDS_API_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

    best: dict[str, dict] = {}
    for event in data:
        for bookmaker in event.get("bookmakers", []):
            bk_name = bookmaker.get("title", "")
            for market in bookmaker.get("markets", []):
                if market.get("key") != "outrights":
                    continue
                for outcome in market.get("outcomes", []):
                    team_raw = (outcome.get("name") or "").strip()
                    price = outcome.get("price", 0)
                    if not team_raw or not price:
                        continue
                    team = _NAME_MAP.get(team_raw, team_raw)
                    if team not in best or price > best[team]["best_odds"]:
                        flag, _ = _TEAM_META.get(team, ("🏳️", 99))
                        best[team] = {
                            "team": team,
                            "flag": flag,
                            "best_odds": price,
                            "bookmaker": bk_name,
                        }

    result = sorted(best.values(), key=lambda x: x["best_odds"])
    await set_cached("wc_winner_bookmakers_v1", result, ttl=3600)
    return result
