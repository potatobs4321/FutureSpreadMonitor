import time

from PyQt5.QtCore import pyqtSignal, QTimer, QObject
from futu import *

from Callbacks import OrderBookCallback
from FutuAPI.APIContext import APIContext
from GlobalEvents import GlobalEvents, ID_GlobalEvent_Login_Success, ID_GlobalEvent_Login_Failed, \
    ID_GlobalEvent_App_Exit
from Util import UtilFuncs


class FutureSymbol:
    def __init__(self, symbol, volume):
        self.sym = symbol
        self.vol = volume

    def __repr__(self):
        return "sym={}, vol={}".format(self.sym, self.vol)


class FutuAPIContext(QObject, APIContext):
    _data_signal = pyqtSignal(dict)
    _is_inited_ = False
    _qot_context_ = None
    _trd_contexts_ = dict()
    _connect_timer_ = QTimer()
    _connect_start_time = 0

    def init_connect(self, ip, port):
        if self._qot_context_ is not None:
            return
        self._is_inited_ = True
        self._qot_context_ = OpenQuoteContext(ip, port, is_async_connect=True)
        self._connect_start_time = time.time()
        self._connect_timer_.timeout.connect(self.on_connect_check_timer)
        self._connect_timer_.start(200)
        GlobalEvents.register_event(ID_GlobalEvent_App_Exit, self.close)

    def on_recv_orderbook(self, data):
        self._data_signal.emit(data)

    def on_recv_self_signal(self, signal):
        if signal == "connect_check":
            pass

    def on_connect_check_timer(self):
        cur_time = time.time()
        if self._connect_start_time > 0 and cur_time - self._connect_start_time > 10:
            self._qot_context_.close()
            self._qot_context_ = None
            self._connect_timer_.stop()
            GlobalEvents.notify_event(ID_GlobalEvent_Login_Failed)
        if self._qot_context_ is None:
            return
        if self._qot_context_.status == ContextStatus.READY:  # 连接成功
            # 行情连接创建成功后，直接创建交易连接
            # 交易连接没有异步参数，只能同步创建，如果行情连接创建成功了，交易连接默认可以创建成功
            self.init_trade_contexts()
            self._handler = OrderBookCallback(self.on_recv_orderbook)
            self._qot_context_.set_handler(self._handler)
            self._connect_timer_.stop()
            GlobalEvents.notify_event(ID_GlobalEvent_Login_Success)
            return

    def subscribe(self, symbol_list, sub_list):
        if self._qot_context_ is None:
            return "连接未创建"
        ret, data = self._qot_context_.subscribe(symbol_list, sub_list)
        if ret != RET_OK:
            print(data)
            return data
        return ""

    def unsubscribe_all(self):
        if self._qot_context_ is None:
            return "连接未创建"
        ret, data = self._qot_context_.unsubscribe_all()
        if ret != RET_OK:
            print(data)
            return data
        return ""

    def get_future_list(self, future_symbol):
        if self._qot_context_ is None:
            return "连接未创建"
        ret, data = self._qot_context_.get_referencestock_list(future_symbol, SecurityReferenceType.FUTURE)
        if ret != RET_OK:
            print('get_referencestock_list:', data)
            return []
        future_list = data['code'].values.tolist()
        filtered_list = [item for item in future_list if not UtilFuncs.is_linked_future_contract(item)]
        print(filtered_list)
        ret, data = self._qot_context_.get_market_snapshot(filtered_list)
        if ret != RET_OK:
            print('get_market_snapshot:', data)
            return []
        ret_list = []
        for index, row in data.iterrows():
            ret_list.append(FutureSymbol(row["code"], row["volume"]))
        return ret_list

    def init_trade_contexts(self):
        pass

    def close(self, _=None):
        if self._qot_context_ is not None:
            self._qot_context_.close()
