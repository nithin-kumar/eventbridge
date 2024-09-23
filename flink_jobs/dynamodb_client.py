import boto3


class DynamoDBClientSingleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DynamoDBClientSingleton, cls).__new__(cls, *args, **kwargs)
            cls._instance.dynamodb = boto3.resource('dynamodb', aws_access_key_id="dummy", aws_secret_access_key="dummy", region_name='us-west-2', endpoint_url='http://dynamodb:8000')
        return cls._instance

    def get_table(self, table_name):
        return self.dynamodb.Table(table_name)