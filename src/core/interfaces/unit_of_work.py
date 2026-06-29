from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.interfaces.repositories import (
    IPaymentsRepository,
    IOutboxRepository,
)


class IUnitOfWork(ABC):
    session: AsyncSession
    payments_repo: IPaymentsRepository
    outbox_repo: IOutboxRepository

    @abstractmethod
    async def __aenter__(self):
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc, tb):
        pass
