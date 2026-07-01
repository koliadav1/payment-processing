import uuid

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import String, DateTime, Uuid, func
from sqlalchemy import Enum as SQLEnum
from datetime import datetime
from enum import Enum
from typing import Any, Dict

from src.core.database import Base


class OutboxEventStatus(Enum):
    PENDING = "pending"
    PROCESSED = "processed"


class OutboxEvent(Base):
    __tablename__ = "outbox"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    payload: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    status: Mapped[OutboxEventStatus] = mapped_column(
        SQLEnum(OutboxEventStatus),
        nullable=False,
        default=OutboxEventStatus.PENDING,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
