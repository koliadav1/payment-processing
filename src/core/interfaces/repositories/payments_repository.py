from abc import abstractmethod

from src.models.payments import Payment
from .base_repository import IRepository


class IPaymentsRepository(IRepository[Payment]):
    @abstractmethod
    async def get_by_idempotency_key(
        self, idempotency_key: str
    ) -> Payment | None:
        """Получение оплаты по ключу уникальности"""
        pass
