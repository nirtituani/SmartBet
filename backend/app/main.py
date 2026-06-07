import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as v1_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    from app.services.warmup import warm_cache
    asyncio.create_task(warm_cache())
    yield


app = FastAPI(title="SmartBet API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_router, prefix="/api/v1")


@app.get("/test-lineups")
async def test_lineups():
    """Test whether API-Football lineups endpoint is accessible on current plan."""
    import httpx
    from app.core.config import settings
    if not settings.football_api_key:
        return {"error": "FOOTBALL_API_KEY not set"}
    # Use England vs Croatia (fixture 67) as a test — happening June 17
    # We first need to find the real API-Football fixture ID
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Fetch WC 2026 fixtures for June 17
            r = await client.get(
                "https://api-football-v1.p.rapidapi.com/v3/fixtures",
                headers={
                    "X-RapidAPI-Key": settings.football_api_key,
                    "X-RapidAPI-Host": settings.football_api_host,
                },
                params={"league": 1, "season": 2026, "date": "2026-06-17"},
            )
            data = r.json()
            fixtures = data.get("response", [])
            if not fixtures:
                return {"error": "no fixtures found", "raw": data}
            # Try lineups for the first fixture found
            fixture_id = fixtures[0]["fixture"]["id"]
            r2 = await client.get(
                "https://api-football-v1.p.rapidapi.com/v3/fixtures/lineups",
                headers={
                    "X-RapidAPI-Key": settings.football_api_key,
                    "X-RapidAPI-Host": settings.football_api_host,
                },
                params={"fixture": fixture_id},
            )
            return {
                "fixture_id": fixture_id,
                "fixture_teams": f"{fixtures[0]['teams']['home']['name']} vs {fixtures[0]['teams']['away']['name']}",
                "lineup_status": r2.status_code,
                "lineup_response": r2.json(),
            }
    except Exception as e:
        return {"error": str(e)}


@app.get("/health")
async def health():
    from app.core.cache import _redis
    from app.core.config import settings
    from app.core.budget import get_spend, DAILY_LIMIT_USD
    redis_ok = False
    if _redis is not None:
        try:
            await _redis.ping()
            redis_ok = True
        except Exception:
            pass
    spend = await get_spend()
    return {
        "status": "ok",
        "ai_enabled": bool(settings.anthropic_api_key),
        "redis_connected": redis_ok,
        "daily_spend_usd": round(spend, 3),
        "daily_limit_usd": DAILY_LIMIT_USD,
    }
