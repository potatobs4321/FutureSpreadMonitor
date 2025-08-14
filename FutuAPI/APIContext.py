from abc import abstractmethod

from PyQt5.QtCore import pyqtSignal


class APIContext:
    _api_signals_ = pyqtSignal(str)
    @abstractmethod
    def init_connect(self, ip, port):
        pass

    @abstractmethod
    def on_recv_orderbook(self, data):
        pass

    @abstractmethod
    def subscribe(cls, symbol_list, sub_list):
        pass

    @abstractmethod
    def unsubscribe_all(cls):
        pass

    @abstractmethod
    def get_future_list(self, future_symbol):
        pass

    @abstractmethod
    def close(self):
        pass

class ContextMgr:
    _impl_ = None

    @classmethod
    def init_api_context(cls, api_context):
        cls._impl_ = api_context

    @classmethod
    def get_api_context(cls):
        return cls._impl_

    @classmethod
    def init_connect(cls, ip, port):
        if cls._impl_ is not None:
            cls._impl_.init_connect(ip, port)

    @classmethod
    def subscribe(cls, symbol_list, sub_list):
        if cls._impl_ is not None:
            return cls._impl_.subscribe(symbol_list, sub_list)
        return "API对象未创建！"

    @classmethod
    def unsubscribe_all(cls):
        if cls._impl_ is not None:
            return cls._impl_.unsubscribe_all()
        return "API对象未创建！"

    @classmethod
    def get_future_list(cls, future_symbol):
        if cls._impl_ is not None:
            return cls._impl_.get_future_list(future_symbol)
        return "API对象未创建！"

    @classmethod
    def close(cls):
        if cls._impl_ is not None:
            return cls._impl_.close()
        return "API对象未创建！"
