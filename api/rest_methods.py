import requests
from api.api_strategy import APIStrategy
from common.constants import API_TIMEOUT


class GETStrategy(APIStrategy):
    def execute(self, url, data=None, headers=None):
        response = requests.get(url, params=data, headers=headers, timeout=API_TIMEOUT)
        response.raise_for_status()
        return response

class POSTStrategy(APIStrategy):
    def execute(self, url, data=None, headers=None):
        response = requests.post(url, json=data, headers=headers, timeout=API_TIMEOUT)
        response.raise_for_status()
        return response

class PUTStrategy(APIStrategy):
    def execute(self, url, data=None, headers=None):
        response = requests.put(url, json=data, headers=headers, timeout=API_TIMEOUT)
        response.raise_for_status()
        return response

class PATCHStrategy(APIStrategy):
    def execute(self, url, data=None, headers=None):
        response = requests.patch(url, json=data, headers=headers, timeout=API_TIMEOUT)
        response.raise_for_status()
        return response