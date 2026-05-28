from fastapi import APIRouter
from app.api.v1.endpoints.matches import router as matches_router

router = APIRouter()
router.include_router(matches_router)
