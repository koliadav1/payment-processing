import asyncio
import random

from faststream import FastStream
from faststream.rabbit import (
    ExchangeType,
    RabbitBroker,
    RabbitMessage,
    RabbitQueue,
    RabbitExchange,
)
from httpx import AsyncClient

from src.schemas.payments import PaymentEventPayload
from src.core.config import settings
from src.utils.dependencies import get_uow
from src.models.payments import PaymentStatus
from src.publisher import MAIN_QUEUE_NAME

broker = RabbitBroker(settings.RABBITMQ_URL)
app = FastStream(broker)

main_queue = RabbitQueue(MAIN_QUEUE_NAME, durable=True)

RETRY_DELAYS_MS = [2000, 4000, 8000]
RETRY_EXCHANGE = "x-payments-retries"

retry_queues = []

retry_exchange = RabbitExchange(
    name=RETRY_EXCHANGE, type=ExchangeType.DIRECT, durable=True
)

for i, delay in enumerate(RETRY_DELAYS_MS, start=1):
    rq = RabbitQueue(
        f"payments.retry.{i}",
        durable=True,
        arguments={
            "x-message-ttl": delay,
            "x-dead-letter-exchange": RETRY_EXCHANGE,
            "x-dead-letter-routing-key": MAIN_QUEUE_NAME,
        },
    )
    retry_queues.append(rq)


@app.after_startup
async def setup():
    x = await broker.declare_exchange(retry_exchange)
    q = await broker.declare_queue(main_queue)
    await q.bind(x, routing_key=MAIN_QUEUE_NAME)

    for rq in retry_queues:
        await broker.declare_queue(rq)


@broker.subscriber(main_queue)
async def handle_payment_event(event: PaymentEventPayload, msg: RabbitMessage):
    headers = msg.headers or {}
    curr_retry = int(headers.get("x-retry-count", 0))

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
        if chance < 0.8:
            if curr_retry < len(RETRY_DELAYS_MS):
                next_retry = curr_retry + 1
                target_queue = f"payments.retry.{next_retry}"
                headers["x-retry-count"] = next_retry

                await broker.publish(
                    message=event, queue=target_queue, headers=headers
                )
            else:
                # TODO dql
                raise Exception("Temp exception")
            return

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
            await client.post(
                url=str(payment.webhook_url), json=webhook_data, timeout=5
            )
    except Exception as e:
        print(
            f"Не удалось отправить уведомление на webhook {payment.webhook_url}, ошибка: {e}"
        )
