import asyncio
import random

from faststream import FastStream
from faststream.rabbit import RabbitBroker, RabbitQueue
from httpx import AsyncClient

from src.schemas.payments import PaymentEventPayload
from src.core.config import settings
from src.utils.dependencies import get_uow
from src.models.payments import PaymentStatus

broker = RabbitBroker(settings.RABBITMQ_URL)
app = FastStream(broker)

main_queue = RabbitQueue("payments.new", durable=True)


@broker.subscriber(main_queue)
async def handle_payment_event(event: PaymentEventPayload):
    uow = await get_uow()
    async with uow:
        payment = await uow.payments_repo.get(event.id)

        if not payment:
            return
        if payment.status == PaymentStatus.SUCCEEDED:
            return

        processing_time = random.uniform(2.0, 5.0)
        await asyncio.sleep(processing_time)

        chance = random.random()
        if chance < 0.1:
            # TODO retries, dlq
            raise Exception("Temp exception")

        payment.status = PaymentStatus.SUCCEEDED
        await uow.payments_repo.update(payment)

    webhook_data = {
        "payment_id": str(payment.id),
        "status": "succeeded",
        "amount": str(payment.amount),
        "currency": payment.currency.value,
    }

    try:
        async with AsyncClient() as client:
            response = await client.post(
                url=str(payment.webhook_url), json=webhook_data, timeout=5
            )
    except Exception as e:
        print(
            f"Не удалось отправить уведомление на webhook {payment.webhook_url}, ошибка: {e}"
        )
