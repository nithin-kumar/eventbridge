import json
import logging
import os

from confluent_kafka import Consumer, KafkaError

from events.handlers.event_status_update_handler import EventStatusUpdateHandlerHandler
from webflow.settings import KAFKA_EVENTS_STATUS_UPDATE_TOPIC, KAFKA_EVENTS_DISPATCH_STATUS_UPDATE_GROUP, \
    KAFKA_BOOTSTRAP_SERVERS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

event_status_update_handler = EventStatusUpdateHandlerHandler()
def consume_messages():
    consumer = Consumer({
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'group.id': KAFKA_EVENTS_DISPATCH_STATUS_UPDATE_GROUP,
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': True,
        'auto.commit.interval.ms': 2000
    })

    consumer.subscribe([KAFKA_EVENTS_STATUS_UPDATE_TOPIC])

    try:
        while True:
            msgs = consumer.consume(num_messages=10, timeout=1.0)
            if msgs is None:
                continue
            for msg in msgs:
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        logger.error("Consumer error: %s", msg.error())
                        continue

                event_data = json.loads(msg.value().decode('utf-8'))
                event_status_update_handler.handle(event_data)


    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

if __name__ == "__main__":
    consume_messages()