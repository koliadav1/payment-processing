from datetime import datetime, timezone
import uuid

from typing import Annotated, Any, Dict
from pydantic import AfterValidator, BaseModel, ConfigDict, Field, HttpUrl
from decimal import Decimal

from src.models.payments import Currency, PaymentStatus


def validate_utc(v: datetime) -> datetime:
    if v.tzinfo is None:
        return v.replace(tzinfo=timezone.utc)
    return v.astimezone(timezone.utc)


UtcDateTime = Annotated[datetime, AfterValidator(validate_utc)]


class PaymentCreate(BaseModel):
    amount: Decimal = Field(
        ...,
        decimal_places=2,
        gt=0,
        lt=99999999.99,
        description="Сумма платежа",
    )
    currency: Currency = Field(default=Currency.RUB, description="Валюта")
    description: str | None = Field(
        None, max_length=1024, description="Описание"
    )
    payment_metadata: Dict[str, Any] | None = Field(
        None, description="Метаданные"
    )
    webhook_url: HttpUrl = Field(
        ..., description="URL для уведомления по платежу"
    )


class PaymentResponse(BaseModel):
    id: uuid.UUID
    status: PaymentStatus
    created_at: UtcDateTime


class PaymentReadResponse(PaymentResponse):
    amount: Decimal
    currency: Currency
    description: str | None
    payment_metadata: Dict[str, Any] | None
    webhook_url: str
    processed_at: UtcDateTime

    model_config = ConfigDict(from_attributes=True)
