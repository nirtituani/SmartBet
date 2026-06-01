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
    raw = os.environ.get("ANTHROPIC_API_KEY", "NOT IN ENV")
    return {
        "status": "ok",
        "ai_enabled": bool(settings.anthropic_api_key),
        "key_prefix": settings.anthropic_api_key[:10] if settings.anthropic_api_key else "NOT SET",
        "raw_env": raw[:10] if raw != "NOT IN ENV" else raw,
    }
