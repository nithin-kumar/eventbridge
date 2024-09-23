from api.rest_methods import GETStrategy, POSTStrategy, PUTStrategy, PATCHStrategy
from api.rest_strategy import RESTStrategy
from api.soap_strategy import SOAPStrategy
from common.enums import APIStrategyType


class APIStrategyFactory:
    @staticmethod
    def get_api_strategy(api_strategy_type):
        if api_strategy_type == APIStrategyType.REST_GET.value:
            return RESTStrategy(GETStrategy())
        elif api_strategy_type == APIStrategyType.REST_POST.value:
            return RESTStrategy(POSTStrategy())
        elif api_strategy_type == APIStrategyType.REST_PUT.value:
            return RESTStrategy(PUTStrategy())
        elif api_strategy_type == APIStrategyType.REST_PATCH.value:
            return RESTStrategy(PATCHStrategy())
        elif api_strategy_type == APIStrategyType.SOAP.value:
            return SOAPStrategy()
        else:
            raise ValueError("Invalid strategy type")