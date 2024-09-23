import logging

from events.handlers.base_handler import BaseHandler
from events.services import update_event_connection_state

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
class EventStatusUpdateHandlerHandler(BaseHandler):
    def _handle(self, event_data):
        try:
            update_event_connection_state(event_data.get('event_connection_id'), event_data.get('status'), event_data.get('http_code'))
            logger.info("Updated the status of event connection: %s", event_data.get('event_connection_id'))
        except Exception as e:
            logger.error("Failed to update the status of event connection: %s , error %s", event_data.get('event_connection_id'), e)

