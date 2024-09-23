class SourceDTO:
    def __init__(self, id, account_id, name, created_at, updated_at):
        self.id = id
        self.account_id = account_id
        self.name = name
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self):
        return {
            'id': self.id,
            'account_id': self.account_id,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }

class ConnectionDTO:
    def __init__(self, id, account_id, name, destination_id, source_id, api_strategy_type, state, namespace):
        self.id = id
        self.account_id = account_id
        self.name = name
        self.destination_id = destination_id
        self.source_id = source_id
        self.api_strategy_type = api_strategy_type
        self.state = state
        self.namespace = namespace


    def to_dict(self):
        return {
            'id': self.id,
            'account_id': self.account_id,
            'name': self.name,
            'destination_id': self.destination_id,
            'source_id': self.source_id,
            'api_strategy_type': self.api_strategy_type,
            'state': self.state,
            'namespace': self.namespace,
        }


class DestinationDTO:
    def __init__(self, id, account_id, name, endpoint, authentication_credentials):
        self.id = id
        self.account_id = account_id
        self.name = name
        self.endpoint = endpoint
        self.authentication_credentials = authentication_credentials

    def to_dict(self):
        return {
            'id': self.id,
            'account_id': self.account_id,
            'name': self.name,
            'endpoint': self.endpoint,
            'authentication_credentials': self.authentication_credentials,
        }


class AccountDTO:
    def __init__(self, id, name, retention_period):
        self.id = id
        self.name = name
        self.retention_period = retention_period

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'retention_period': self.retention_period,
        }