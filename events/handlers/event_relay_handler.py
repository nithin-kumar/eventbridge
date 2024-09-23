import json
import logging

from common.enums import ConnectionState
from events.handlers.base_handler import BaseHandler
from events.services import get_event_connections
from userhook.services import get_connection_by_id
from utils.kafka_producer import KafkaProducerSingleton
from webflow.settings import KAFKA_EVENTS_DISPATCH_TOPIC

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

producer = KafkaProducerSingleton().producer

class EventRelayHandler(BaseHandler):
    def _handle(self, event_data):
        """
        Handles the relay of event data.

        This function retrieves all event connections for the given event and pushes each connection
        to a Kafka topic for further processing. It ensures that only active connections are relayed.

        Args:
            event_data (dict): The event data containing account_id and event_id.

        Raises:
            Exception: If there is an error during the event relay process.
        """
        try:
            account_id = event_data.get('account_id')
            event_connections = get_event_connections(event_data.get('event_id'))
            for event_connection in event_connections:
                #TODO: move this to cache ?
                connection_dto = get_connection_by_id(event_connection.get('connection_id'))
                if connection_dto.get('state') != ConnectionState.ON.value:
                    logger.info("Connection is not active: %s", event_connection.get('id'))
                    continue
                payload = {
                    'event_connection_id': str(event_connection.get('id')),
                }
                producer.produce(KAFKA_EVENTS_DISPATCH_TOPIC, key=str(account_id), value=json.dumps(payload))
            producer.flush()
            logger.info("Events are pushed to Kafka: %s", event_data)
        except Exception as e:
            logger.error("Failed to relay event: %s", e)