import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as v1_router


_REFRESH_INTERVAL = 12 * 60 * 60  # 12 hours in seconds


async def _warmup_loop():
    from app.services.warmup import warm_cache
    while True:
        await warm_cache()
        await asyncio.sleep(_REFRESH_INTERVAL)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    asyncio.create_task(_warmup_loop())
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
    raw = os.environ.get("ANTHROPIC_API_KEY", "NOT IN ENV")
    return {
        "status": "ok",
        "ai_enabled": bool(settings.anthropic_api_key),
        "key_prefix": settings.anthropic_api_key[:10] if settings.anthropic_api_key else "NOT SET",
        "raw_env": raw[:10] if raw != "NOT IN ENV" else raw,
    }
