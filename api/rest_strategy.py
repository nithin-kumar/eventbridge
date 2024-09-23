from api.api_strategy import APIStrategy

class RESTStrategy(APIStrategy):
    def __init__(self, method_strategy):
        self.method_strategy = method_strategy

    def execute(self, url, data=None, headers=None):
        return self.method_strategy.execute(url, data, headers)