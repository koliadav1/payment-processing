from datetime import datetime, timezone
import uuid
from typing import List
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.outbox import OutboxEvent, OutboxEventStatus
from src.core.interfaces.repositories.outbox_repository import (
    IOutboxRepository,
)


class OutboxRepository(IOutboxRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, outbox: OutboxEvent) -> None:
        """Сохранить событие в outbox"""
        self._session.add(outbox)
        await self._session.flush()
        await self._session.refresh(outbox)

    async def get_pending(self, limit: int = 100) -> List[OutboxEvent]:
        """Получить события для публикации"""
        query = (
            select(OutboxEvent)
            .where(OutboxEvent.status == OutboxEventStatus.PENDING)
            .order_by(OutboxEvent.created_at.asc())
            .limit(limit)
        )

        result = await self._session.execute(query)
        return result.scalars().all()

    async def mark_as_processed(self, outbox_event: OutboxEvent) -> None:
        """Пометить событие как обработанное"""
        outbox_event.status = OutboxEventStatus.PROCESSED
        outbox_event.processed_at = datetime.now(timezone.utc)
        await self._session.flush()
