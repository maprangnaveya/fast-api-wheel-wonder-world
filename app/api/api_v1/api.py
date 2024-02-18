from fastapi import APIRouter

from .endpoints.auth import router as auth_router
from .endpoints.broker import router as broker_router


router = APIRouter()

router.include_router(auth_router)
router.include_router(broker_router)
