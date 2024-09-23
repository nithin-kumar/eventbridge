from userhook.models import Source, Connection, Destination, Account
from userhook.dto import SourceDTO, ConnectionDTO, DestinationDTO, AccountDTO

def get_source_by_id(source_id):
    try:
        source = Source.get(source_id)
        source_dto = SourceDTO(
            id=source.id,
            account_id=source.account_id,
            name=source.name,
            created_at=source.created_at,
            updated_at=source.updated_at
        )
        return source_dto.to_dict()
    except Source.DoesNotExist:
        return None
    except Exception as e:
        raise e


def get_connections_by_account_and_source(account_id, source_id):
    try:
        connections = Connection.account_source_index.query(account_id, range_key_condition=Connection.source_id == source_id)
        connection_dtos = [
            ConnectionDTO(
                id=conn.id,
                account_id=conn.account_id,
                name=conn.name,
                destination_id=conn.destination_id,
                source_id=conn.source_id,
                api_strategy_type=conn.api_strategy_type,
                state=conn.state,
            ).to_dict() for conn in connections
        ]
        return connection_dtos
    except Exception as e:
        raise e


def get_connection_by_id(connection_id):
    try:
        connection = Connection.get(connection_id)
        connection_dto = ConnectionDTO(
            id=connection.id,
            account_id=connection.account_id,
            name=connection.name,
            destination_id=connection.destination_id,
            source_id=connection.source_id,
            api_strategy_type=connection.api_strategy_type,
            state=connection.state,
        )
        return connection_dto.to_dict()
    except Connection.DoesNotExist:
        return None
    except Exception as e:
        raise e


def get_destination_by_id(destination_id):
    try:
        destination = Destination.get(destination_id)
        destination_dto = DestinationDTO(
            id=destination.id,
            account_id=destination.account_id,
            name=destination.name,
            endpoint=destination.endpoint,
            authentication_credentials=destination.authentication_credentials,
        )
        return destination_dto.to_dict()
    except Destination.DoesNotExist:
        return None
    except Exception as e:
        raise e


def create_account(name, retention_period, username, password):
    try:
        account = Account(
            name=name,
            retention_period=retention_period,
            username=username,
            password=password
        )
        account.save()
        return account.id
    except Exception as e:
        raise e


def get_account_by_id(account_id):
    try:
        account = Account.get(account_id)
        account_dto = AccountDTO(
            id=account.id,
            name=account.name,
            retention_period=account.retention_period
        )
        return account_dto.to_dict()
    except Account.DoesNotExist:
        return None
    except Exception as e:
        raise e