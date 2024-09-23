import hashlib
import json

from events.handlers.event_persistence_handler import EventPersistenceHandler
from events.handlers.event_relay_handler import EventRelayHandler
from events.services import get_idempotency_by_id, insert_idempotency


class EventIngestionHandler:
    _instance = None
    _next_handler = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(EventIngestionHandler, cls).__new__(cls, *args, **kwargs)
            cls._instance.build_chain()
        return cls._instance

    def build_chain(self):
        self.event_persistance_handler = EventPersistenceHandler()
        self.event_relay_handler = EventRelayHandler()

        self.event_persistance_handler.set_next(self.event_relay_handler)

    def handle(self, event_data):
        idempotency_key = event_data.get('source_id') + hashlib.sha256(json.dumps(event_data.get('payload')).encode('utf-8')).hexdigest()

        idempotency_obj = get_idempotency_by_id(idempotency_key)
        if idempotency_obj:
            return idempotency_obj.get('response')

        self.event_persistance_handler.handle(event_data)
        insert_idempotency(idempotency_key, event_data.get('account_id'),
                           {'status': 'success', 'message': 'Event persisted successfully'})
