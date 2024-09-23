from abc import ABC, abstractmethod

class APIStrategy(ABC):
    @abstractmethod
    def execute(self, url, data=None, headers=None):
        pass


