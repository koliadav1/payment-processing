import uuid
from typing import TYPE_CHECKING, Any, Dict

from src.models.outbox import OutboxEvent

if TYPE_CHECKING:
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
        async with uow:
            event = OutboxEvent(
                id=uuid.uuid4(),
                event_type=event_type,
                payload=payload,
            )

            await uow.outbox_repo.save(event)
