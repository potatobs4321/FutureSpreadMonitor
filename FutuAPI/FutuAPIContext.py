import time

from PyQt5.QtCore import pyqtSignal, QTimer, QObject
from futu import *

from FutuAPI.APIContext import APIContext
from GlobalEvents import GlobalEvents, ID_GlobalEvent_Login_Success, ID_GlobalEvent_Login_Failed, \
    ID_GlobalEvent_App_Exit


class FutuAPIContext(APIContext):
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
            self._connect_timer_.stop()
            GlobalEvents.notify_event(ID_GlobalEvent_Login_Success)
            return

    def init_trade_contexts(self):
        pass

    def close(self, _):
        if self._qot_context_ is not None:
            self._qot_context_.close()
