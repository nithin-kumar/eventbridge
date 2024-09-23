# python
import logging

from userhook import get_connections_by_account_and_source
from .base_handler import BaseHandler
from events.services import insert_event, batch_insert_event_connections

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EventPersistenceHandler(BaseHandler):
    def _handle(self, event_data):
        """
        Handles the persistence of event data.

        This function inserts the event data into the database and associates it with
        the relevant connections. If the event is successfully saved, it updates the
        event data with the event ID for further processing by the next handler.

        Args:
            event_data (dict): The event data containing source_id, account_id, header, and payload.

        Raises:
            Exception: If there is an error during the event persistence process.
        """
        try:
            event = insert_event(event_data.get('source_id'),
                                 event_data.get('account_id'), event_data.get('header'), event_data.get('payload'))

            connections = get_connections_by_account_and_source(event_data.get('account_id'),
                                                                event_data.get('source_id'))

            batch_insert_event_connections(connections, event)
            logger.info("Saved event to DynamoDB: %s", event_data)
            # This is important for the next handler to know the event id
            event_data['event_id'] = event.id
        except Exception as e:
            logger.error("Failed to save event to DynamoDB: %s", e)
