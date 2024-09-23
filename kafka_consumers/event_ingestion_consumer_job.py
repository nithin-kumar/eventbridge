import json
import logging
import os

from confluent_kafka import Consumer, KafkaError

from common.constants import KAFKA_EVENTS_INGESTION_TOPIC

from utils.event_ingestion_handler import EventIngestionHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

event_ingestion_handler = EventIngestionHandler()

def consume_messages():
    consumer = Consumer({
        'bootstrap.servers': os.environ["KAFKA_BROKER"],
        'group.id': os.environ["KAFKA_GROUP"],
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': True,
        'auto.commit.interval.ms': 2000
    })

    consumer.subscribe(list(KAFKA_EVENTS_INGESTION_TOPIC.values()))

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
                event_ingestion_handler.handle(event_data)

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()


if __name__ == "__main__":
    consume_messages()
