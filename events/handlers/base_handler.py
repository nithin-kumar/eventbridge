from abc import ABC, abstractmethod

class BaseHandler(ABC):
    def __init__(self):
        self.next_handler = None

    def set_next(self, handler):
        self.next_handler = handler
        return handler

    def handle(self, event):
        self._handle(event)
        if self.next_handler:
            self.next_handler.handle(event)
        return

    @abstractmethod
    def _handle(self, event):
        pass