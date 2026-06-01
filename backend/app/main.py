from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as v1_router

app = FastAPI(title="SmartBet API", version="1.0.0")

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
    from app.core.config import settings
    return {
        "status": "ok",
        "ai_enabled": bool(settings.anthropic_api_key),
        "key_prefix": settings.anthropic_api_key[:10] if settings.anthropic_api_key else "NOT SET",
    }
