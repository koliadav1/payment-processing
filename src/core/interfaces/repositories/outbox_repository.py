from abc import abstractmethod, ABC
from typing import List
import uuid

from src.models.outbox import OutboxEvent


class IOutboxRepository(ABC):
    @abstractmethod
    async def save(self, outbox: OutboxEvent) -> OutboxEvent:
        """Сохранить событие в outbox"""
        pass

    @abstractmethod
    async def get_pending(self, limit: int = 100) -> List[OutboxEvent]:
        """Получить события для публикации"""
        pass

    @abstractmethod
    async def mark_as_processed(self, outbox_id: uuid.UUID) -> None:
        """Пометить событие как обработанное"""
        pass
