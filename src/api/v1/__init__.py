from fastapi import APIRouter
from .payment import router as payment_router

router = APIRouter(prefix="/api/v1")
router.include_router(payment_router)
