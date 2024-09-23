from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from common.enums import KafkaRetentionPeriod, APIStrategyType
from userhook.models import Source, Destination, Connection, Account
import json

from userhook.services import create_account
from utils.common_utils import create_jwt_token


@csrf_exempt
def connection(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            account_id = data.get('account_id')
            source_name = data.get('source_name')
            destination_name = data.get('destination_name')
            destination_endpoint = data.get('destination_endpoint')
            destination_auth_credentials = data.get('destination_authentication_credentials')
            connection_name = source_name + "-" + destination_name
            api_strategy_type = data.get('api_strategy_type')
            namespace = data.get('namespace')

            if not all([source_name, destination_endpoint, destination_auth_credentials, destination_name, api_strategy_type]):
                return JsonResponse({'status': 'error', 'message': 'Missing required parameters'}, status=400)

            if api_strategy_type not in APIStrategyType._value2member_map_:
                return JsonResponse({'status': 'error', 'message': 'Invalid api_strategy_type'}, status=400)

            source = next(Source.account_name_index.query(account_id, range_key_condition=Source.name == source_name), None)
            if not source:
                source = Source(account_id=account_id,name=source_name)
                source.save()

            destination = next(Destination.account_name_index.query(account_id, range_key_condition=Destination.name == destination_name), None)
            if not destination:
                destination = Destination(
                    account_id=account_id,
                    name=destination_name,
                    endpoint=destination_endpoint,
                    authentication_credentials=destination_auth_credentials
                )
                destination.save()

            if next(Connection.account_name_index.query(account_id, range_key_condition=Connection.name == connection_name), None):
                return JsonResponse({'status': 'error', 'message': 'Connection already exists'}, status=400)
            else:
                # Create Connection
                connection = Connection(
                    source_id=source.id,
                    account_id=account_id,
                    name=connection_name,
                    destination_id=destination.id,
                    api_strategy_type=api_strategy_type,
                    namespace=namespace,
                )
                connection.save()

            return JsonResponse(
                {'status': 'success', 'message': 'Connection created successfully', 'connection_id': connection.source_id},
                status=201)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'An error occurred: ' + str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)



@csrf_exempt
def signup(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            retention_period = data.get('retention_period')
            username = data.get('username')
            password = data.get('password')

            if not all([name, retention_period, username, password]):
                return JsonResponse({'status': 'error', 'message': 'Missing required parameters'}, status=400)

            if retention_period not in KafkaRetentionPeriod._value2member_map_:
                return JsonResponse({'status': 'error', 'message': 'Invalid retention period'}, status=400)

            account_id = create_account(name, retention_period, username, password)
            return JsonResponse({'status': 'success', 'message': 'Account created successfully', 'account_id': str(account_id)}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'An error occurred: ' + str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


@csrf_exempt
def status(request):
    if request.method == 'GET':
        JsonResponse({'status': 'success', 'message': 'Userhook is running'}, status=200)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
