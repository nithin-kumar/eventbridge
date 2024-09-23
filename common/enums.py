from enum import Enum


class EventConnectionStatus(Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


class APIStrategyType(Enum):
    REST_GET = "REST_GET"
    REST_POST = "REST_POST"
    REST_PUT = "REST_PUT"
    REST_DELETE = "REST_DELETE"
    REST_PATCH = "REST_PATCH"
    SOAP = "SOAP"


class KafkaRetentionPeriod(Enum):
    ONE_DAY = "1d"
    THREE_DAYS = "3d"
    SEVEN_DAYS = "7d"
    FOURTEEN_DAYS = "14d"
    THIRTY_DAYS = "30d"


class ConnectionState(Enum):
    ON = "on"
    OFF = "off"
