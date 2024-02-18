from fastapi import APIRouter

from .endpoints.auth import router as auth_router
from .endpoints.broker import router as broker_router
from .endpoints.car import router as car_router
from .endpoints.user import router as user_router

from .endpoints.mockup_data import router as load_mockup_data_router


router = APIRouter()

router.include_router(auth_router)
router.include_router(broker_router)
router.include_router(car_router)
router.include_router(user_router)
router.include_router(load_mockup_data_router)
