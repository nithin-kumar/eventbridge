# This file contains the logic for inserting events and event connections into the database.
import os

from events.dto import EventConnectionDTO, IdempotencyDTO
from events.models import Events, EventConnection, Idempotency


def get_event_by_id(event_id):
    event = Events.get(event_id)
    return {
        'id': event.id,
        'account_id': event.account_id,
        'payload': event.payload,
        'header': event.header,
        'source_id': event.source_id,
        'created_at': event.created_at,
        'updated_at': event.updated_at
    }


def insert_event(source_id, account_id, header, payload):
    event = Events(
        account_id=account_id,
        payload=payload,
        header=header,
        source_id=source_id,
    )
    event.save()
    return event


def batch_insert_event_connections(connections_dto, event):
    for connection_dto in connections_dto:
        event_connection = EventConnection(
            account_id=connection_dto.get('account_id'),
            source_id=connection_dto.get('source_id'),
            event_id=event.id,
            connection_id=connection_dto.get('id'),
        )
        event_connection.save()


def get_event_connections(event_id):
    event_connections = EventConnection.event_index.query(event_id)
    return [EventConnectionDTO(
        id=ec.id,
        account_id=ec.account_id,
        source_id=ec.source_id,
        event_id=ec.event_id,
        connection_id=ec.connection_id,
        retry_count=ec.retry_count,
        delivery_code=ec.delivery_code,
        created_at=ec.created_at,
        updated_at=ec.updated_at
    ).to_dict() for ec in event_connections]


def get_event_connection_by_id(event_connection_id):
    ec = EventConnection.get(event_connection_id)
    return EventConnectionDTO(
        id=ec.id,
        account_id=ec.account_id,
        source_id=ec.source_id,
        event_id=ec.event_id,
        connection_id=ec.connection_id,
        retry_count=ec.retry_count,
        delivery_code=ec.delivery_code,
        created_at=ec.created_at,
        updated_at=ec.updated_at
    ).to_dict()


def update_event_connection_retry_count(event_connection_id):
    ec = EventConnection.get(event_connection_id)
    ec.retry_count += 1
    ec.save()
    return ec


def get_idempotency_by_id(unique_key):
    try:
        idempotency_record = Idempotency.get(unique_key)
        return IdempotencyDTO(
            unique_key=idempotency_record.unique_key,
            account_id=idempotency_record.account_id,
            response=idempotency_record.response
        ).to_dict()
    except Idempotency.DoesNotExist:
        return


def insert_idempotency(unique_key, account_id, response):
    idempotency_record = Idempotency(
        unique_key=unique_key,
        account_id=account_id,
        response=response,
    )
    idempotency_record.save()


def update_event_connection_state(event_connection_id, new_state, http_code):
    ec = EventConnection.get(event_connection_id)
    ec.status = new_state
    ec.delivery_code = http_code
    ec.save()
    return ec


def get_event_connections_filtered(account_id, start_time, end_time, limit, last_evaluated_key, source=None, status=None):
    event_connections = EventConnection.account_created_index.query(
        account_id,
        range_key_condition=(EventConnection.created_at.between(start_time, end_time)),
        limit=limit,
        last_evaluated_key=last_evaluated_key
    )
    # Filter by status and source
    if status:
        event_connections = [ec for ec in event_connections if ec.status == status]
    if source:
        event_connections = [ec for ec in event_connections if ec.source_id == source]

    return [EventConnectionDTO(
        id=ec.id,
        account_id=ec.account_id,
        source_id=ec.source_id,
        event_id=ec.event_id,
        connection_id=ec.connection_id,
        retry_count=ec.retry_count,
        delivery_code=ec.delivery_code,
        created_at=ec.created_at,
        updated_at=ec.updated_at
    ).to_dict() for ec in event_connections]
