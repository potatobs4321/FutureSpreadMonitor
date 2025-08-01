from abc import abstractmethod

from PyQt5.QtCore import pyqtSignal


class APIContext:
    _api_signals_ = pyqtSignal(str)
    @abstractmethod
    def init_connect(self, ip, port):
        pass

class ContextMgr:
    _impl_ = None

    @classmethod
    def init_api_context(cls, api_context):
        cls._impl_ = api_context

    @classmethod
    def init_connect(cls, ip, port):
        if cls._impl_ is not None:
            cls._impl_.init_connect(ip, port)
