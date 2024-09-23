import importlib
import inspect
import os

import boto3
import django
from django.apps import apps
from django.conf import settings
from pynamodb.models import Model

from webflow.settings import DYNAMODB_ENDPOINT, DYNAMODB_REGION, DYNAMODB_ACCESS_KEY, DYNAMODB_SECRET_KEY

settings.configure()
django.setup()


def get_models():
    models = []
    modules = ['events.models', 'userhook.models']
    for module_name in modules:
        module = importlib.import_module(module_name)
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, Model) and obj is not Model:
                models.append(obj)
    return models


if __name__ == '__main__':
    for model in get_models():
        print(model)
        model.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)
        print(model.exists())
