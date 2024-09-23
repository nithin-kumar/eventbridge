import json
import logging

import requests

from api.api_strategy_factory import APIStrategyFactory
from common.constants import MAX_RETRY_LIMIT
from common.enums import EventConnectionStatus
from common.exceptions import MaxRetriesReached
from events.handlers.base_handler import BaseHandler
from events.services import get_event_connection_by_id, update_event_connection_retry_count, get_idempotency_by_id, \
    insert_idempotency, get_event_by_id
from userhook.services import get_connection_by_id, get_destination_by_id
from utils.kafka_producer import KafkaProducerSingleton
from webflow.settings import KAFKA_EVENTS_STATUS_UPDATE_TOPIC, KAFKA_EVENTS_DISPATCH_TOPIC

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

producer = KafkaProducerSingleton().producer

class EventDispatchHandler(BaseHandler):

    def _handle(self, event_data):
        """
        Handles the event dispatch process.

        This function processes the event data, retrieves necessary details,
        checks for idempotency, and executes the API strategy. If any exception
        occurs during the process, it handles the dispatch failure.

        Args:
            event_data (dict): The event data containing event_connection_id.

        Returns:
            The response from the idempotency object if it exists, otherwise None.
        """

        event_connection_id = event_data.get('event_connection_id')
        if not event_connection_id:
            logger.warning("No event_connection_id found in event_data")
            return

        try:
            event_connection_dto = get_event_connection_by_id(event_connection_id)
            idempotency_key = event_connection_id + str(event_connection_dto.get('retry_count'))
            idempotency_obj = get_idempotency_by_id(idempotency_key)
            if idempotency_obj:
                return idempotency_obj.get('response')

            event_dto = get_event_by_id(event_connection_dto.get('event_id'))
            logger.info("EventConnection: %s - %s", event_connection_dto.get('id'), event_connection_dto.get('retry_count'))
            connection_dto = get_connection_by_id(event_connection_dto.get('connection_id'))
            destination_dto = get_destination_by_id(connection_dto.get('destination_id'))
            api_strategy = APIStrategyFactory.get_api_strategy(connection_dto.get('api_strategy_type'))
            self._execute_api_strategy(api_strategy, destination_dto, event_dto, event_connection_id,
                                       event_connection_dto)
            insert_idempotency(idempotency_key, event_connection_dto.get('account_id'), {'status': 'success'})
        except Exception as e:
            self._handle_dispatch_failure(event_connection_id, event_connection_dto, e)

    def _execute_api_strategy(self, api_strategy, destination_dto, event_dto, event_connection_id,
                              event_connection_dto):
        try:
            # TODO: create headers, User credentials has to be stored on a Secure storage. Get it and pass it back as headers
            response = api_strategy.execute(destination_dto.get('endpoint'), event_dto.get('payload').as_dict())
            payload = {
                'event_connection_id': str(event_connection_id),
                'status': EventConnectionStatus.SUCCESS.value,
                'http_code': response.status_code
            }
            producer.produce(KAFKA_EVENTS_STATUS_UPDATE_TOPIC, key=str(event_connection_dto.get("account_id")),
                             value=json.dumps(payload))
            logging.info("Successfully updated the status of event connection")
        except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as req_err:
            logging.error("Request error occurred: %s -%s", event_connection_id, event_connection_dto.get('retry_count'))
            self._handle_request_exception(event_connection_id, event_connection_dto, req_err)

    def _handle_request_exception(self, event_connection_id, event_connection_dto, req_err):
        retry_count = int(event_connection_dto.get('retry_count', 0))
        if retry_count < MAX_RETRY_LIMIT:
            logging.info("Retrying the event connection id %s", event_connection_id)
            update_event_connection_retry_count(event_connection_id)
            payload = {
                'event_connection_id': str(event_connection_id),
            }
            producer.produce(KAFKA_EVENTS_DISPATCH_TOPIC, key=str(event_connection_dto.get("account_id")),
                             value=json.dumps(payload))
        else:
            """
            SSLError(SSLCertVerificationError) does not have http response code. Hence it can be empty
            """
            status_code = req_err.response.status_code if req_err.response else None
            self._handle_dispatch_failure(event_connection_id, event_connection_dto, MaxRetriesReached(retries=retry_count), status_code)
        logger.error("Request error occurred: %s", req_err)

    def _handle_dispatch_failure(self, event_connection_id, event_connection_dto, e, error_code=None):
        payload = {
            'event_connection_id': str(event_connection_id),
            'status': EventConnectionStatus.FAILED.value,
            'http_code': error_code
        }
        producer.produce(KAFKA_EVENTS_STATUS_UPDATE_TOPIC,
                         key=str(event_connection_dto.get("account_id")),
                         value=json.dumps(payload))
        logger.error("Failed to dispatch event: %s", e)
