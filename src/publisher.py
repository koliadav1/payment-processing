import asyncio
from faststream import FastStream
from faststream.rabbit import (
    ExchangeType,
    RabbitBroker,
    RabbitExchange,
    RabbitQueue,
)

from src.core.config import settings
from src.utils.dependencies import get_uow

BATCH_SIZE = 100
POLL_INTERVAL = 5

MAIN_QUEUE_NAME = "payments.new"

broker = RabbitBroker(settings.RABBITMQ_URL)
payment_exchange = RabbitExchange(
    name="x-payments-new", type=ExchangeType.DIRECT, durable=True
)
payment_queue = RabbitQueue(name=MAIN_QUEUE_NAME, durable=True)
payment_publisher = broker.publisher(
    queue=payment_queue, exchange=payment_exchange
)

app = FastStream(broker)


async def outbox_polling_loop():
    while True:
        try:
            uow = await get_uow()
            async with uow:
                events = await uow.outbox_repo.get_pending(BATCH_SIZE)

                if not events:
                    await asyncio.sleep(POLL_INTERVAL)
                    continue

                print(f"[Outbox] Найдено {len(events)} событий для отправки")

                for event in events:
                    event_uow = await get_uow()
                    async with event_uow:
                        await payment_publisher.publish(
                            message=event.payload,
                            headers={
                                "event_type": event.event_type,
                                "outbox_id": str(event.id),
                            },
                        )

                        await event_uow.outbox_repo.mark_as_processed(event)
            await asyncio.sleep(POLL_INTERVAL)
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"Outbox publisher error: {e}")
            await asyncio.sleep(POLL_INTERVAL)


@app.after_startup
async def start_outbox_publisher():
    x = await broker.declare_exchange(payment_exchange)
    q = await broker.declare_queue(payment_queue)

    await q.bind(x, routing_key=MAIN_QUEUE_NAME)

    asyncio.create_task(outbox_polling_loop())
