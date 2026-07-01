import uuid
from typing import Any, Dict

from src.models.outbox import OutboxEvent
from src.core.interfaces.unit_of_work import IUnitOfWork


class OutboxMethods:
    """Статические методы для работы с outbox"""

    @staticmethod
    async def save_event(
        event_type: str, payload: Dict[str, Any], uow: IUnitOfWork
    ) -> None:
        """
        Создание нового события в outbox
        """
        event = OutboxEvent(
            id=uuid.uuid4(),
            event_type=event_type,
            payload=payload,
        )

        await uow.outbox_repo.save(event)
