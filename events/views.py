import datetime
import hashlib

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import json

from common.constants import KAFKA_EVENTS_INGESTION_TOPIC
from events.models import EventConnection
from events.services import get_idempotency_by_id, insert_idempotency, update_event_connection_retry_count, \
    get_event_connection_by_id
from userhook import get_source_by_id
from userhook.services import get_account_by_id, get_connection_by_id
from utils.kafka_producer import KafkaProducerSingleton

from webflow.settings import KAFKA_EVENTS_DISPATCH_TOPIC

producer = KafkaProducerSingleton().producer
@csrf_exempt
def  handle_event(request, id):
    if request.method == 'POST':
        try:
            source_dto = get_source_by_id(id)
            if source_dto is None:
                return JsonResponse({'status': 'error', 'message': 'Source not found'}, status=400)

            account_dto = get_account_by_id(source_dto.get('account_id'))
            if not account_dto:
                raise ValueError(f"Account with ID {source_dto.get('account_id')} not found")

            retention_period = account_dto.get('retention_period')
            kafka_topic = KAFKA_EVENTS_INGESTION_TOPIC.get(retention_period)
            if not kafka_topic:
                raise ValueError(f"Kafka topic for retention period {retention_period} not found")

            # Serialize the event using Protocol Buffers
            # event_proto = event_pb2.Event(
            #     connection_id=event.connection_id,
            #     account_id=event.account_id,
            #     payload={k: event_pb2.Value(str_value=str(v)) for k, v in event.payload.items()},
            #     header={k: event_pb2.Value(str_value=str(v)) for k, v in event.header.items()}
            # )
            #print("Serialized message bytes: %s", event_proto.SerializeToString())
            # producer.produce(KAFKA_EVENTS_INGESTION_TOPIC, key=str(event.account_id),
            #                  value=event_proto.SerializeToString())

            payload = {
                'source_id': source_dto.get('id'),
                'account_id': str(source_dto.get('account_id')),
                'payload': json.loads(request.body),
                'header': dict(request.headers)
            }

            #TODO: How costly the following operation ?
            idempotency_key = source_dto.get('id') + hashlib.sha256(request.body).hexdigest()

            idempotency_obj = get_idempotency_by_id(idempotency_key)
            if idempotency_obj:
                return JsonResponse(idempotency_obj.get('response').as_dict(), status=200)

            producer.produce(kafka_topic, key=str(source_dto.get("account_id")), value=json.dumps(payload))
            producer.flush()

            success_response = {'status': 'success', 'message': 'Event inserted successfully'}
            insert_idempotency(idempotency_key, source_dto.get('account_id'), success_response)

            return JsonResponse(success_response, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'An error occurred: ' + str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


@csrf_exempt
def retry_event_connection(request, event_connection_id):
    if request.method == 'POST':
        try:
            if not event_connection_id:
                return JsonResponse({'status': 'error', 'message': 'Missing event_connection_id'}, status=400)

            update_event_connection_retry_count(event_connection_id)

            event_connection_dto = get_event_connection_by_id(event_connection_id)
            payload = {
                'event_connection_id': str(event_connection_id),
            }
            producer.produce(KAFKA_EVENTS_DISPATCH_TOPIC, key=str(event_connection_dto.get('account_id')), value=json.dumps(payload))
            producer.flush()

            return JsonResponse({'status': 'success', 'message': 'Event Connection retried successfully'}, status=200)
        except EventConnection.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Event connection not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'An error occurred: ' + str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)



@csrf_exempt
def events(request):
    if request.method == 'GET':
        account_id = request.GET.get('account_id')
        status = request.GET.get('status')
        source = request.GET.get('source')
        limit = max(100, int(request.GET.get('limit', 10)))
        last_evaluated_key = request.GET.get('last_evaluated_key')

        start_timestamp = datetime.datetime.fromisoformat(request.GET.get('start_timestamp', '1970-01-01T00:00:00'))
        end_timestamp = datetime.datetime.fromisoformat(
            request.GET.get('end_timestamp', datetime.datetime.utcnow().isoformat()))

        if not account_id:
            return JsonResponse({'status': 'error', 'message': 'Missing required parameter: account_id'}, status=400)

        try:

            event_connections = EventConnection.account_created_index.query(
                account_id,
                range_key_condition=(EventConnection.created_at.between(start_timestamp, end_timestamp)),
                limit=limit,
                last_evaluated_key=last_evaluated_key
            )

            # Filter by status and source
            if status:
                event_connections = [ec for ec in event_connections if ec.status == status]
            if source:
                event_connections = [ec for ec in event_connections if ec.source_id == source]

            # Create the list of maps
            event_connections_list = []
            for ec in event_connections:
                connection = get_connection_by_id(ec.connection_id)
                connection_name = connection.get('name')
                connection_namespace = connection.get('namespace')
                event_connections_list.append({
                    'event_connection_id': ec.id,
                    'created_at': ec.created_at,
                    'status': ec.status,
                    'connection_name': connection_name,
                    'retry_count': ec.retry_count,
                    'event_id': ec.event_id,
                    'http_code': ec.delivery_code,
                    'namespace': connection_namespace,
                })
            paginator = Paginator(event_connections_list, limit)
            page = paginator.page(1)

            return JsonResponse({'status': 'success', 'event_connections': list(page), 'last_evaluated_key': event_connections.last_evaluated_key}, status=200)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'An error occurred: ' + str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)