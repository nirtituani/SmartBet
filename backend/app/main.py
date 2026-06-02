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


@app.get("/health")
async def health():
    import os
    from app.core.config import settings
    from app.core.cache import _redis
    raw = os.environ.get("ANTHROPIC_API_KEY", "NOT IN ENV")
    redis_ok = False
    if _redis is not None:
        try:
            await _redis.ping()
            redis_ok = True
        except Exception:
            pass
    return {
        "status": "ok",
        "ai_enabled": bool(settings.anthropic_api_key),
        "redis_connected": redis_ok,
    }
