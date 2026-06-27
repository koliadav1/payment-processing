import uuid

from fastapi import APIRouter, Depends, HTTPException, Header, Request, status

from src.core.interfaces.unit_of_work import IUnitOfWork
from src.services.payment_service import PaymentService
from src.models.payments import User
from src.schemas.users import (
    PaymentReadResponse,
    PaymentResponse,
    PaymentCreate,
)
from src.utils.dependencies import get_uow, verify_api_key

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post(
    "/",
    response_model=PaymentResponse,
    status_code=202,
    summary="Создание платежа",
    description="Создает новый платеж",
)
async def create_payment(
    payment_data: PaymentCreate,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    payment_service: PaymentService = Depends(),
    uow: IUnitOfWork = Depends(get_uow),
    _: bool = Depends(verify_api_key),
):
    """
    Создание нового платежа
    """
    payment = await payment_service.create_payment(
        amount=payment_data.amount,
        idempotency_key=idempotency_key,
        webhook_url=payment_data.webhook_url,
        uow=uow,
        currency=payment_data.currency,
        description=payment_data.description,
        payment_metadata=payment_data.payment_metadata,
    )

    return PaymentResponse(payment.id, payment.status, payment.created_at)


@router.get(
    "/{payment_id}",
    summary="Получить оплату по UUID",
    response_model=PaymentReadResponse,
)
async def get_payment(
    payment_id: uuid.UUID,
    payment_service: PaymentService = Depends(),
    uow: IUnitOfWork = Depends(get_uow),
    _: bool = Depends(verify_api_key),
):
    """Получить данные об оплате по ее UUID"""
    payment = await payment_service.get_payment(payment_id, uow)
    return payment
