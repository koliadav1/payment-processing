from sqlalchemy import select

from src.core.interfaces.repositories.payments_repository import (
    IPaymentsRepository,
)
from src.models.payments import Payment
from .base_repository import SQLRepository


class PaymentsRepository(IPaymentsRepository, SQLRepository):
    def __init__(self, session):
        super().__init__(session, Payment)

    async def get_by_idempotency_key(
        self, idempotency_key: str
    ) -> Payment | None:
        """Получение оплаты по ключу уникальности"""
        stmt = select(Payment).where(
            idempotency_key == Payment.idempotency_key
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
