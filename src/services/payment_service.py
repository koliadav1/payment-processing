import uuid

from src.models.payments import Payment, Currency
from src.core.exceptions import PaymentAlreadyExistsError, PaymentNotFoundError
from src.core.interfaces.unit_of_work import IUnitOfWork
from .dependencies import OutboxMethods


class PaymentService:
    async def create_payment(
        self,
        amount: float,
        idempotency_key: str,
        webhook_url: str,
        uow: IUnitOfWork,
        currency: Currency = Currency.RUB,
        description: str | None = None,
        payment_metadata: dict | None = None,
    ) -> Payment:
        """
        Создание нового платежа
        """
        async with uow:
            existing_payment = await uow.payments_repo.get_by_idempotency_key(
                idempotency_key
            )
            if existing_payment:
                raise PaymentAlreadyExistsError(
                    "Payment with this idempotency key already exists"
                )

            payment = Payment(
                amount=amount,
                currency=currency,
                description=description,
                payment_metadata=payment_metadata,
                idempotency_key=idempotency_key,
                webhook_url=str(webhook_url),
            )

            added_payment = await uow.payments_repo.add(payment)

            event_payload = {
                "id": str(added_payment.id),
                "amount": str(added_payment.amount),
                "currency": added_payment.currency.value,
                "description": added_payment.description,
                "payment_metadata": added_payment.payment_metadata,
                "webhook_url": added_payment.webhook_url,
                "created_at": added_payment.created_at.isoformat(),
            }

            await OutboxMethods.save_event(
                event_type="payment_created", payload=event_payload, uow=uow
            )

            return added_payment

    async def get_payment(
        self, payment_id: uuid.UUID, uow: IUnitOfWork
    ) -> Payment:
        async with uow:
            payment = await uow.payments_repo.get(payment_id)
            if not payment:
                raise PaymentNotFoundError("Payment with this uuid not found")

            return payment
