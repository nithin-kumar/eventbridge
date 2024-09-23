import datetime
import uuid

from pynamodb.attributes import UnicodeAttribute, MapAttribute, UTCDateTimeAttribute, NumberAttribute
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection
from pynamodb.models import Model
from pynamodb_attributes import UUIDAttribute

from common.enums import EventConnectionStatus
from webflow.settings import DYNAMODB_ENDPOINT, DYNAMODB_REGION, DYNAMODB_ACCESS_KEY, DYNAMODB_SECRET_KEY


class EventAccountIndex(GlobalSecondaryIndex):
    """
    This class represents a global secondary index
    """
    class Meta:
        index_name = 'events-by-account-index'
        read_capacity_units = 2
        write_capacity_units = 1
        projection = AllProjection()

    account_id = UUIDAttribute(hash_key=True)
class Events(Model):
    class Meta:
        table_name = 'events'
        region = DYNAMODB_REGION
        aws_access_key_id = DYNAMODB_ACCESS_KEY
        aws_secret_access_key = DYNAMODB_SECRET_KEY
        host = DYNAMODB_ENDPOINT

    id = UUIDAttribute(default=uuid.uuid4, hash_key=True)
    account_id = UUIDAttribute()
    source_id = UnicodeAttribute()
    payload = MapAttribute()
    header = MapAttribute()
    created_at = UTCDateTimeAttribute(default=datetime.datetime.utcnow)
    updated_at = UTCDateTimeAttribute(default=datetime.datetime.utcnow)

    account_index = EventAccountIndex()


class EventConnectionAccountCreatedIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = 'event-connections-by-account-index'
        read_capacity_units = 2
        write_capacity_units = 1
        projection = AllProjection()

    account_id = UUIDAttribute(hash_key=True)
    created_at = UTCDateTimeAttribute(range_key=True)

class EventConnectionAccountSourceIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = 'event-connections-by-account-source-index'
        read_capacity_units = 2
        write_capacity_units = 1
        projection = AllProjection()

    account_id = UUIDAttribute(hash_key=True)
    source_id = UnicodeAttribute(range_key=True)

class EventConnectionEventIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = 'event-connections-by-event-index'
        read_capacity_units = 2
        write_capacity_units = 1
        projection = AllProjection()

    event_id = UUIDAttribute(hash_key=True)


class EventConnection(Model):
    class Meta:
        table_name = 'event_connections'
        region = DYNAMODB_REGION
        aws_access_key_id = DYNAMODB_ACCESS_KEY
        aws_secret_access_key = DYNAMODB_SECRET_KEY
        host = DYNAMODB_ENDPOINT

    id=UUIDAttribute(default=uuid.uuid4, hash_key=True)
    account_id = UUIDAttribute()
    event_id = UUIDAttribute()
    connection_id = UUIDAttribute()
    source_id = UnicodeAttribute()
    status = UnicodeAttribute(default=EventConnectionStatus.PENDING.value)
    delivery_code = NumberAttribute(null=True)
    retry_count = NumberAttribute(default=0)
    created_at = UTCDateTimeAttribute(default=datetime.datetime.utcnow)
    updated_at = UTCDateTimeAttribute(default=datetime.datetime.utcnow)

    account_created_index = EventConnectionAccountCreatedIndex()
    account_source_index = EventConnectionAccountSourceIndex()
    event_index = EventConnectionEventIndex()



class Idempotency(Model):
    class Meta:
        table_name = 'idempotency'
        region = DYNAMODB_REGION
        aws_access_key_id = DYNAMODB_ACCESS_KEY
        aws_secret_access_key = DYNAMODB_SECRET_KEY
        host = DYNAMODB_ENDPOINT

    unique_key = UnicodeAttribute(hash_key=True)
    account_id = UUIDAttribute()
    response = MapAttribute()
    created_at = UTCDateTimeAttribute(default=datetime.datetime.utcnow)
    updated_at = UTCDateTimeAttribute(default=datetime.datetime.utcnow)