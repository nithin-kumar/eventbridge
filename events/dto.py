from pynamodb_attributes import UUIDAttribute

from pynamodb.attributes import UnicodeAttribute, MapAttribute, UTCDateTimeAttribute, NumberAttribute
class EventDTO():
    id = UUIDAttribute()
    connection_id = UnicodeAttribute()
    account_id = UUIDAttribute()
    payload = MapAttribute()
    header = MapAttribute()
    delivery_code = NumberAttribute()
    status = UnicodeAttribute()
    created_at = UTCDateTimeAttribute()
    updated_at = UTCDateTimeAttribute()


class EventConnectionDTO:
    def __init__(self, id, account_id, source_id, event_id, connection_id, retry_count, delivery_code, created_at, updated_at):
        self.id = id
        self.account_id = account_id
        self.source_id = source_id
        self.event_id = event_id
        self.connection_id = connection_id
        self.retry_count = retry_count
        self.delivery_code = delivery_code
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self):
        return {
            'id': self.id,
            'account_id': self.account_id,
            'source_id': self.source_id,
            'event_id': self.event_id,
            'connection_id': self.connection_id,
            'retry_count': self.retry_count,
            'delivery_code': self.delivery_code,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }


class IdempotencyDTO:
    def __init__(self, unique_key, account_id, response):
        self.unique_key = unique_key
        self.account_id = account_id
        self.response = response

    def to_dict(self):
        return {
            'unique_key': self.unique_key,
            'account_id': self.account_id,
            'response': self.response,
        }