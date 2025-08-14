from PyQt5.QtCore import QObject, pyqtSignal
from enum import Enum
from FutuAPI.APIContext import ContextMgr
from Util import Ring, UtilFuncs
from futu import SubType


class MonitorStatus(Enum):
    Stopped = 0
    Monitoring = 1

class FutureSpreadSignal(Enum):
    StatusChanged = 1
    OrderBookUpdate = 2
    FinishPullFutureList = 3

class FutureSpreadModel(QObject):
    _model_signal = pyqtSignal(FutureSpreadSignal)

    def __init__(self):
        super().__init__()
        ContextMgr.get_api_context()._data_signal.connect(self.on_recv_orderbook_signal)
        self._checked = False
        self.cur_sym = None
        self.cur_bid = None
        self.cur_ask = None
        self.next_sym = None
        self.next_bid = None
        self.next_ask = None
        self.buy_ring = Ring(100000)
        self.sell_ring = Ring(100000)
        self.api_status = MonitorStatus.Stopped
        self._checked = False
        self._future_base = UtilFuncs.get_future_symbol_str()
        self._last_future = None
        self._future_list = []

    def start_monitor(self):
        print('subscribe:', self.cur_sym, ", ", self.next_sym)
        sub_ret = ContextMgr.subscribe([self.cur_sym, self.next_sym], [SubType.ORDER_BOOK])
        if len(sub_ret) == 0:
            self.update_status(MonitorStatus.Monitoring)

    def stop_monitor(self):
        sub_ret = ContextMgr.unsubscribe_all()
        if len(sub_ret) == 0:
            self.update_status(MonitorStatus.Stopped)

    def get_buy_spread_list(self):
        return self.buy_ring.to_list()

    def get_sell_spread_list(self):
        return self.sell_ring.to_list()

    def set_future_base_symbol(self, future_base):
        if self._future_base != future_base:
            self._future_base = future_base
            UtilFuncs.set_future_symbol_str(self._future_base)

    def get_future_base_symbol(self):
        return self._future_base

    def pull_future_list(self):
        if self._future_base != self._last_future:
            self._future_list = ContextMgr.get_future_list(self._future_base)
            self._last_future = self._future_base
            self.emit_signal(FutureSpreadSignal.FinishPullFutureList)

    def get_future_related_symbols(self):
        return self._future_list

    def set_current_symbol(self, symbol):
        self.cur_sym = symbol

    def set_next_symbol(self, symbol):
        self.next_sym = symbol

    def set_checked(self, checked):
        self._checked = checked

    def emit_signal(self, signal):
        self._model_signal.emit(signal)

    def update_status(self, status):
        if self.api_status != status:
            self.api_status = status
            self.emit_signal(FutureSpreadSignal.StatusChanged)

    def get_status(self):
        return self.api_status

    def on_recv_orderbook_signal(self, data):
        if not self.update_bid_ask(data):
            return
        self.update_spread_ring()
        if self._checked:
            self.print_ask_bid_prices()
        self.emit_signal(FutureSpreadSignal.OrderBookUpdate)

    def update_bid_ask(self, data):
        if "code" not in data:
            print("data format error, data = ", data)
            return
        _symbol = data["code"]
        data_updated = False
        if _symbol == self.cur_sym:
            if "Bid" in data and len(data["Bid"]) > 0:
                if self.cur_bid != data["Bid"][0][0]:
                    self.cur_bid = data["Bid"][0][0]
                    data_updated = True
            if "Ask" in data and len(data["Ask"]) > 0:
                if self.cur_ask != data["Ask"][0][0]:
                    self.cur_ask = data["Ask"][0][0]
                    data_updated = True
        if _symbol == self.next_sym:
            if "Bid" in data and len(data["Bid"]) > 0:
                if self.next_bid != data["Bid"][0][0]:
                    self.next_bid = data["Bid"][0][0]
                    data_updated = True
            if "Ask" in data and len(data["Ask"]) > 0:
                if self.next_ask != data["Ask"][0][0]:
                    self.next_ask = data["Ask"][0][0]
                    data_updated = True
        return data_updated

    def update_spread_ring(self):
        if self.cur_bid is not None and self.cur_ask is not None and\
            self.next_bid is not None and self.next_ask is not None:
            buy_spread = self.cur_ask - self.next_bid  # buy cur_symbol, sell next_symbol
            sell_spread = self.cur_bid -  self.next_ask  # sell cur_symbol, buy next_symbol
            self.buy_ring.push_back(buy_spread)
            self.sell_ring.push_back(sell_spread)

    def print_ask_bid_prices(self):
        print("=== {}: {} - {}; \t\t{}: {} - {} ===".format(self.cur_sym, self.cur_ask, self.cur_bid, self.next_sym, self.next_ask, self.next_bid))

    def close(self):
        ContextMgr.close()


if __name__ == '__main__':
    pass