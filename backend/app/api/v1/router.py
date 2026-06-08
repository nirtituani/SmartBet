from fastapi import APIRouter
from app.api.v1.endpoints.matches import router as matches_router
from app.api.v1.endpoints.groups import router as groups_router
from app.api.v1.endpoints.odds import router as odds_router

router = APIRouter()
router.include_router(matches_router)
router.include_router(groups_router)
router.include_router(odds_router)
