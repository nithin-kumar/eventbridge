import asyncio
import json
import logging

from confluent_kafka import Consumer, KafkaError

from events.handlers.event_dispatch_handler import EventDispatchHandler
from webflow.settings import KAFKA_EVENTS_DISPATCH_TOPIC, KAFKA_EVENTS_DISPATCH_GROUP, KAFKA_BOOTSTRAP_SERVERS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

event_dispatch_handler = EventDispatchHandler()

async def process_message(msg):
    if msg.error():
        if msg.error().code() == KafkaError._PARTITION_EOF:
            return
        else:
            logger.error("Consumer error: %s", msg.error())
            return

    event_data = json.loads(msg.value().decode('utf-8'))
    event_dispatch_handler.handle(event_data)

async def process_messages(msgs):
    await asyncio.gather(*(process_message(msg) for msg in msgs))

async def consume_messages():
    consumer = Consumer({
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'group.id': KAFKA_EVENTS_DISPATCH_GROUP,
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': True,
        'auto.commit.interval.ms': 2000
    })

    consumer.subscribe([KAFKA_EVENTS_DISPATCH_TOPIC])

    try:
        while True:
            msgs = consumer.consume(num_messages=10, timeout=1.0)
            if not msgs:
                continue
            await process_messages(msgs)

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()


if __name__ == "__main__":
    asyncio.run(consume_messages())