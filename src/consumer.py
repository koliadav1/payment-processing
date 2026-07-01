import asyncio
from datetime import datetime, timezone
import random
from faststream import FastStream, Logger
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
RETRY_EXCHANGE_NAME = "x-payments-retries"
DLQ_TTL = 1000 * 60 * 60 * 24 * 7  # 1 неделя
DLQ_NAME = "payments.dlq"
DLQ_EXCHANGE_NAME = "x-payments-dlq"

retry_queues = []
retry_exchange = RabbitExchange(
    name=RETRY_EXCHANGE_NAME, type=ExchangeType.DIRECT, durable=True
)

dead_queue = RabbitQueue(
    DLQ_NAME, durable=True, arguments={"x-message-ttl": DLQ_TTL}
)
dlq_exchange = RabbitExchange(
    name=DLQ_EXCHANGE_NAME, type=ExchangeType.DIRECT, durable=True
)

for i, delay in enumerate(RETRY_DELAYS_MS, start=1):
    rq = RabbitQueue(
        f"payments.retry.{i}",
        durable=True,
        arguments={
            "x-message-ttl": delay,
            "x-dead-letter-exchange": RETRY_EXCHANGE_NAME,
            "x-dead-letter-routing-key": MAIN_QUEUE_NAME,
        },
    )
    retry_queues.append(rq)


@app.after_startup
async def setup():
    x = await broker.declare_exchange(retry_exchange)
    q = await broker.declare_queue(main_queue)
    await q.bind(x, routing_key=MAIN_QUEUE_NAME)

    dlq_x = await broker.declare_exchange(dlq_exchange)
    dlq = await broker.declare_queue(dead_queue)
    await dlq.bind(dlq_x, routing_key=DLQ_NAME)

    for rq in retry_queues:
        await broker.declare_queue(rq)


@broker.subscriber(main_queue)
async def handle_payment_event(
    event: PaymentEventPayload, msg: RabbitMessage, logger: Logger
):
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
        if chance < 0.1:
            if curr_retry < len(RETRY_DELAYS_MS):
                logger.warning(f"Попытка {curr_retry} провалилась")
                next_retry = curr_retry + 1
                target_queue = f"payments.retry.{next_retry}"
                headers["x-retry-count"] = next_retry

                await broker.publish(
                    message=event, queue=target_queue, headers=headers
                )
            else:
                logger.error(f"Платеж {event.id} не обработан")
                payment.status = PaymentStatus.FAILED
                await uow.payments_repo.update(payment)
                await broker.publish(message=event, queue=dead_queue)
            return
        logger.info(f"Платеж {event.id} обработан успешно")
        payment.status = PaymentStatus.SUCCEEDED
        payment.processed_at = datetime.now(timezone.utc)
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
        logger.error(
            f"Не удалось отправить уведомление на webhook {payment.webhook_url}, ошибка: {e}"
        )
