from confluent_kafka import Producer

from webflow.settings import KAFKA_BOOTSTRAP_SERVERS


class KafkaProducerSingleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(KafkaProducerSingleton, cls).__new__(cls, *args, **kwargs)
            cls._instance._producer = Producer({
                'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
                'group.id': 'flink-group'
            })
        return cls._instance

    @property
    def producer(self):
        return self._instance._producer