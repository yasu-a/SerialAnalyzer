from abc import ABC, abstractmethod


class StatusMessageHandler(ABC):
    @abstractmethod
    def info(self, message: str, tag: str = None):
        raise NotImplementedError()

    @abstractmethod
    def error(self, message: str, tag: str = None):
        raise NotImplementedError()


class NullStatusMessageHandler(StatusMessageHandler):
    def info(self, message: str, tag: str = None):
        pass

    def error(self, message: str, tag: str = None):
        pass


_handler: StatusMessageHandler = NullStatusMessageHandler()


def register_message_handler(handler: StatusMessageHandler):
    global _handler
    _handler = handler


def g_get_status() -> StatusMessageHandler:
    return _handler
