import datetime
import uuid

import base62
from pynamodb.attributes import UnicodeAttribute, UTCDateTimeAttribute
from pynamodb.indexes import AllProjection, GlobalSecondaryIndex
from pynamodb.models import Model
from pynamodb_attributes import UUIDAttribute

from common.enums import ConnectionState
from utils.snowflake_id_generator import SnowflakeIDGeneratorSingleton
from webflow.settings import DYNAMODB_REGION, DYNAMODB_ACCESS_KEY, DYNAMODB_SECRET_KEY, DYNAMODB_ENDPOINT


def generate_snowflake_id():
    return base62.encode(SnowflakeIDGeneratorSingleton().get_snowflake_id())


class ConnectionAccountNameIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = 'connections-by-account-name-index'
        read_capacity_units = 2
        write_capacity_units = 1
        projection = AllProjection()

    account_id = UUIDAttribute(hash_key=True)
    name = UnicodeAttribute(range_key=True)


class ConnectionAccountSourceIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = 'connections-by-account--source-index'
        read_capacity_units = 2
        write_capacity_units = 1
        projection = AllProjection()

    account_id = UUIDAttribute(hash_key=True)
    source_id = UnicodeAttribute(range_key=True)


class Connection(Model):
    class Meta:
        table_name = 'connections'
        region = DYNAMODB_REGION
        aws_access_key_id = DYNAMODB_ACCESS_KEY
        aws_secret_access_key = DYNAMODB_SECRET_KEY
        host = DYNAMODB_ENDPOINT

    id = UUIDAttribute(default=uuid.uuid4, hash_key=True)
    source_id = UnicodeAttribute()
    account_id = UUIDAttribute()
    name = UnicodeAttribute()
    namespace = UnicodeAttribute(default='default')
    destination_id = UUIDAttribute()
    state = UnicodeAttribute(default=ConnectionState.ON.value)
    api_strategy_type = UnicodeAttribute()
    created_at = UTCDateTimeAttribute(default=datetime.datetime.utcnow)
    updated_at = UTCDateTimeAttribute(default=datetime.datetime.utcnow)

    account_name_index = ConnectionAccountNameIndex()
    account_source_index = ConnectionAccountSourceIndex()


class DestinationAccountNameIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = 'destination-by-account-name-index'
        read_capacity_units = 2
        write_capacity_units = 1
        projection = AllProjection()

    account_id = UUIDAttribute(hash_key=True)
    name = UnicodeAttribute(range_key=True)


class Destination(Model):
    class Meta:
        table_name = 'destinations'
        region = DYNAMODB_REGION
        aws_access_key_id = DYNAMODB_ACCESS_KEY
        aws_secret_access_key = DYNAMODB_SECRET_KEY
        host = DYNAMODB_ENDPOINT

    id = UUIDAttribute(default=uuid.uuid4, hash_key=True)
    account_id = UUIDAttribute()
    name = UnicodeAttribute()
    endpoint = UnicodeAttribute()
    authentication_credentials = UnicodeAttribute()
    created_at = UTCDateTimeAttribute(default=datetime.datetime.utcnow)
    updated_at = UTCDateTimeAttribute(default=datetime.datetime.utcnow)

    account_name_index = DestinationAccountNameIndex()


class SourceAccountNameIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = 'source-by-account-name-index'
        read_capacity_units = 2
        write_capacity_units = 1
        projection = AllProjection()

    account_id = UUIDAttribute(hash_key=True)
    name = UnicodeAttribute(range_key=True)


class Source(Model):
    class Meta:
        table_name = 'sources'
        region = DYNAMODB_REGION
        aws_access_key_id = DYNAMODB_ACCESS_KEY
        aws_secret_access_key = DYNAMODB_SECRET_KEY
        host = DYNAMODB_ENDPOINT

    id = UnicodeAttribute(default=generate_snowflake_id, hash_key=True)
    account_id = UUIDAttribute()
    name = UnicodeAttribute()
    created_at = UTCDateTimeAttribute(default=datetime.datetime.utcnow)
    updated_at = UTCDateTimeAttribute(default=datetime.datetime.utcnow)

    account_name_index = SourceAccountNameIndex()


class Account(Model):
    class Meta:
        table_name = 'accounts'
        region = DYNAMODB_REGION
        aws_access_key_id = DYNAMODB_ACCESS_KEY
        aws_secret_access_key = DYNAMODB_SECRET_KEY
        host = DYNAMODB_ENDPOINT

    id = UUIDAttribute(default=uuid.uuid4, hash_key=True)
    name = UnicodeAttribute()
    retention_period = UnicodeAttribute()
    created_at = UTCDateTimeAttribute(default=datetime.datetime.utcnow)
    updated_at = UTCDateTimeAttribute(default=datetime.datetime.utcnow)
    username = UnicodeAttribute()
    password = UnicodeAttribute()