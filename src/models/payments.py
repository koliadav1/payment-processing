import uuid

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import String, DateTime, Numeric, Uuid, func
from sqlalchemy import Enum as SQLEnum
from datetime import datetime
from enum import Enum
from decimal import Decimal
from typing import Any, Dict

from src.core.database import Base


class Currency(Enum):
    RUB = "rub"
    USD = "usd"
    EUR = "eur"


class PaymentStatus(Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2), nullable=False
    )
    currency: Mapped[Currency] = mapped_column(
        SQLEnum(Currency), default=Currency.RUB, nullable=False
    )
    description: Mapped[str] = mapped_column(String(1024), nullable=True)
    payment_metadata: Mapped[Dict[str, Any] | None] = mapped_column(
        JSONB, nullable=True
    )
    status: Mapped[PaymentStatus] = mapped_column(
        SQLEnum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING
    )
    idempotency_key: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    webhook_url: Mapped[str] = mapped_column(String(512), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
