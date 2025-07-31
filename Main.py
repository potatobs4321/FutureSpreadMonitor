from datetime import datetime, timedelta

from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt5.QtWidgets import *
import pyqtgraph as pg
from enum import Enum

import pandas as pd

pd.options.display.max_rows=5000
pd.options.display.max_columns=5000
pd.options.display.width=1000
pd.options.display.max_colwidth=1000

from futu import *
from Util import Ring, UtilFuncs
from Callbacks import OrderBookCallback
from Constants import *


class APIStatus(Enum):
    STOPPED = 0
    CONNECTING = 1
    CONNECTED = 2
    MONITORING = 3


class SelfSignal(Enum):
    UPDATE_ORDERBOOK = "UPDATE_ORDERBOOK"
    CHECK_CONNECT = "CHECK_CONNECT"
    UPDATE_MONITOR_TIME = "UPDATE_MONITOR_TIME"
    ADDRESS_EDIT_CHANGED = "ADDRESS_EDIT_CHANGED"
    PORT_EDIT_CHANGED = "PORT_EDIT_CHANGED"
    FUTURE_SYMBOL_EDIT_CHANGED = "FUTURE_SYMBOL_EDIT_CHANGED"


class MyApp(QWidget):
    __self_signal = pyqtSignal(SelfSignal)
    __data_signal = pyqtSignal(dict)
    def __init__(self):
        super().__init__()
        self.setup_api()
        self.setup_ui()

    def setup_api(self):
        self.api_status = APIStatus.STOPPED
        self.qot_ctx = None
        self.info_timer = QTimer()
        self.info_timer.timeout.connect(lambda: self.__self_signal.emit(SelfSignal.UPDATE_MONITOR_TIME))

    def setup_ui(self):
        self.sub_status = QWidget(self)
        sub_status_layout = QHBoxLayout()
        self.api_status_text = QLabel("当前状态：")
        self.api_status_enum = QLabel("--")
        self.total_sub_text = QLabel("    总订阅额度：")
        self.total_sub_num = QLabel("--")
        self.remain_sub_text = QLabel("    剩余订阅额度：")
        self.remain_sub_num = QLabel("--")
        self.monitor_start_time_text = QLabel("    监控开始时间：")
        self.monitor_start_time_str = QLabel("--")
        self.monitor_used_time_text = QLabel("    已监控：")
        self.monitor_used_time_str = QLabel("--")
        sub_status_layout.addWidget(self.api_status_text)
        sub_status_layout.addWidget(self.api_status_enum)
        sub_status_layout.addWidget(self.total_sub_text)
        sub_status_layout.addWidget(self.total_sub_num)
        sub_status_layout.addWidget(self.remain_sub_text)
        sub_status_layout.addWidget(self.remain_sub_num)
        sub_status_layout.addWidget(self.monitor_start_time_text)
        sub_status_layout.addWidget(self.monitor_start_time_str)
        sub_status_layout.addWidget(self.monitor_used_time_text)
        sub_status_layout.addWidget(self.monitor_used_time_str)
        sub_status_layout.setSpacing(8)
        sub_status_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))
        self.sub_status.setLayout(sub_status_layout)

        self.interaction_edit = QWidget(self)
        interaction_edit_layout = QHBoxLayout()
        self.ip_text = QLabel("IP：")
        self.port_text = QLabel("端口：")
        self.future_symbol_text = QLabel("期货合约：")
        self.front_symbol_text = QLabel("近月合约：")
        self.back_symbol_text = QLabel("远月合约：")
        self.update_combobox_btn = QPushButton("获取所有合约")
        self.update_combobox_btn.clicked.connect(self.pull_future_list)
        self.ip_address_edit = QTextEdit()
        self.ip_address_edit.setFixedSize(150, 30)
        self.ip_address_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ip_address_edit.setText(UtilFuncs.get_address_str())
        self.ip_address_edit.textChanged.connect(lambda: self.__self_signal.emit(SelfSignal.ADDRESS_EDIT_CHANGED))
        self.port_edit = QTextEdit()
        self.port_edit.setFixedSize(150, 30)
        self.port_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.port_edit.setText(UtilFuncs.get_port_str())
        self.port_edit.textChanged.connect(lambda: self.__self_signal.emit(SelfSignal.PORT_EDIT_CHANGED))
        self.future_symbol_edit = QTextEdit()
        self.future_symbol_edit.setFixedSize(150, 30)
        self.future_symbol_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.future_symbol_edit.setText(UtilFuncs.get_future_symbol_str())
        self.future_symbol_edit.textChanged.connect(lambda: self.__self_signal.emit(SelfSignal.FUTURE_SYMBOL_EDIT_CHANGED))
        self.front_symbol_box = QComboBox()
        self.front_symbol_box.setFixedSize(150, 30)
        self.back_symbol_box = QComboBox()
        self.back_symbol_box.setFixedSize(150, 30)
        interaction_edit_layout.addWidget(self.ip_text)
        interaction_edit_layout.addWidget(self.ip_address_edit)
        interaction_edit_layout.addWidget(self.port_text)
        interaction_edit_layout.addWidget(self.port_edit)
        interaction_edit_layout.addWidget(self.future_symbol_text)
        interaction_edit_layout.addWidget(self.future_symbol_edit)
        interaction_edit_layout.addWidget(self.update_combobox_btn)
        interaction_edit_layout.addWidget(self.front_symbol_box)
        interaction_edit_layout.addWidget(self.back_symbol_box)
        interaction_edit_layout.setSpacing(8)
        interaction_edit_layout.setContentsMargins(0, 0, 0, 0)
        interaction_edit_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))
        self.interaction_edit.setLayout(interaction_edit_layout)
        self.interaction_edit.setFixedHeight(30)
        self.interaction_edit.setContentsMargins(0, 0, 0, 0)

        self.interaction_btn = QWidget(self)
        interaction_btn_layout = QHBoxLayout()
        self.connect_btn = QPushButton("创建连接")
        self.connect_btn.clicked.connect(self.on_connect_button_clicked)
        self.monitor_btn = QPushButton("开始监控")
        self.monitor_btn.clicked.connect(self.on_monitor_button_clicked)
        self.debug_check_box = QCheckBox("控制台输出摆盘价格")
        self.debug_check_box.clicked.connect(self.on_debug_check_box)
        interaction_btn_layout.addWidget(self.connect_btn)
        interaction_btn_layout.addWidget(self.monitor_btn)
        interaction_btn_layout.addWidget(self.debug_check_box)
        interaction_btn_layout.setSpacing(8)
        interaction_btn_layout.setContentsMargins(0, 0, 0, 0)
        interaction_btn_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))
        self.interaction_btn.setLayout(interaction_btn_layout)
        self.interaction_btn.setFixedHeight(30)
        self.interaction_btn.setContentsMargins(0, 0, 0, 0)

        layout = QVBoxLayout()
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setTitle("期货价差", color='b', size='12pt')
        self.buy_spread_line = self.plot_widget.plot(
            [], [],
            pen=pg.mkPen(color='r', width=2),
            name='买入价差'
        )
        self.sell_spread_line = self.plot_widget.plot(
            [], [],
            pen=pg.mkPen(color='g', width=2),
            name='卖出价差'
        )
        self.warning_text = QLabel("连接未创建")
        self.warning_text.setStyleSheet("""
            QLabel {
                color: red;               /* 字体颜色 */
                font-weight: bold;        /* 加粗 */
            }
        """)
        layout.addWidget(self.sub_status)
        layout.addWidget(self.interaction_edit)
        layout.addWidget(self.interaction_btn)
        layout.addWidget(self.plot_widget, 0)
        layout.addWidget(self.warning_text)
        self.setLayout(layout)

        self.__self_signal.connect(self.on_recv_self_signal)
        self.__data_signal.connect(self.on_finish_update_orderbook)
        self.update_api_status()

    def make_connection(self):
        if self.api_status == APIStatus.MONITORING:
            self.update_warning_test("正在监控中！")
            return
        self.update_warning_test("创建连接中...")
        address = self.ip_address_edit.toPlainText()
        port = int(self.port_edit.toPlainText())
        print(address, port)
        self.qot_ctx = OpenQuoteContext(address, port, is_async_connect=True)
        self.api_status = APIStatus.CONNECTING
        self.connect_timer = QTimer()
        self.connect_timer.timeout.connect(lambda: self.__self_signal.emit(SelfSignal.CHECK_CONNECT))
        self.connect_start_time = datetime.now()
        self.connect_timer.start(200)
        self.update_api_status()

    def stop_monitoring(self):
        if self.api_status == APIStatus.STOPPED:
            self.update_warning_test("还未开始监控。")
            return
        self.update_warning_test("监控已停止。")
        ret, data = self.qot_ctx.unsubscribe_all()
        if ret != RET_OK:
            self.update_warning_test(data)
            return
        self.api_status = APIStatus.CONNECTED
        self.update_subscribe_data()
        self.update_api_status()
        self.stop_timer()

    def disconnect_connection(self):
        self.qot_ctx.close()
        self.qot_ctx = None
        self.api_status = APIStatus.STOPPED
        self.total_sub_num.setText("--")
        self.remain_sub_num.setText("--")
        self.update_api_status()
        self.stop_timer()

    def update_api_status(self):
        status_dict = {
            APIStatus.STOPPED: "未连接",
            APIStatus.CONNECTING: "连接中",
            APIStatus.CONNECTED: "已连接",
            APIStatus.MONITORING: "监听中",
        }
        self.api_status_enum.setText(status_dict[self.api_status])
        if self.api_status == APIStatus.STOPPED:
            self.connect_btn.setText("创建连接")
            self.monitor_btn.setEnabled(False)
            self.monitor_btn.setText("开始监听")
            self.update_combobox_btn.setEnabled(False)
            self.front_symbol_box.setEnabled(False)
            self.back_symbol_box.setEnabled(False)
        elif self.api_status == APIStatus.CONNECTING:
            self.connect_btn.setText("断开连接")
            self.monitor_btn.setEnabled(False)
            self.monitor_btn.setText("开始监听")
            self.update_combobox_btn.setEnabled(False)
            self.front_symbol_box.setEnabled(False)
            self.back_symbol_box.setEnabled(False)
        elif self.api_status == APIStatus.CONNECTED:
            self.connect_btn.setText("断开连接")
            self.monitor_btn.setEnabled(True)
            self.monitor_btn.setText("开始监听")
            self.update_combobox_btn.setEnabled(True)
            self.front_symbol_box.setEnabled(True)
            self.back_symbol_box.setEnabled(True)
        elif self.api_status == APIStatus.MONITORING:
            self.connect_btn.setText("断开连接")
            self.monitor_btn.setEnabled(True)
            self.monitor_btn.setText("停止监听")
            self.update_combobox_btn.setEnabled(False)
            self.front_symbol_box.setEnabled(False)
            self.back_symbol_box.setEnabled(False)

    def update_subscribe_data(self):
        ret, sub_status = self.qot_ctx.query_subscription()
        if ret == RET_OK:
            if "total_used" in sub_status:
                self.total_sub_num.setText(str(sub_status["total_used"]))
            if "remain" in sub_status:
                self.remain_sub_num.setText(str(sub_status["remain"]))

    def on_connect_button_clicked(self):
        if self.api_status == APIStatus.STOPPED:
            self.make_connection()
        else:
            self.disconnect_connection()

    def on_monitor_button_clicked(self):
        if self.api_status == APIStatus.CONNECTED:
            self.start_monitoring()
        else:
            self.stop_monitoring()

    def on_recv_orderbook(self, data):
        self.__data_signal.emit(data)

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

    def pull_future_list(self):
        if self.api_status == APIStatus.STOPPED or self.api_status == APIStatus.CONNECTING:
            self.update_warning_test("连接未创建，无法拉取合约资料")
            return
        future_symbol = self.future_symbol_edit.toPlainText()
        ret, data = self.qot_ctx.get_referencestock_list(future_symbol, SecurityReferenceType.FUTURE)
        if ret != RET_OK:
            self.update_warning_test(data)
            return
        future_list = data['code'].values.tolist()
        filtered_list = [item for item in future_list if not UtilFuncs.is_linked_future_contract(item)]
        ret, data = self.qot_ctx.get_market_snapshot(filtered_list)
        if ret != RET_OK:
            self.update_warning_test(data)
            return
        self.front_symbol_box.clear()
        self.back_symbol_box.clear()
        for index, row in data.iterrows():
            item_str = "{}  ({})".format(row["code"], UtilFuncs.number_to_comma_str(row["volume"]))
            self.front_symbol_box.addItem(item_str)
            self.back_symbol_box.addItem(item_str)

        font_metrics = self.front_symbol_box.fontMetrics()
        max_width = max(font_metrics.width(text) for text in [self.front_symbol_box.itemText(i) for i in range(self.front_symbol_box.count())])

        # 设置下拉菜单的最小宽度（额外加一些 padding）
        self.front_symbol_box.view().setMinimumWidth(max_width + 40)
        self.back_symbol_box.view().setMinimumWidth(max_width + 40)


    def on_recv_self_signal(self, sig_type):
        if sig_type == SelfSignal.CHECK_CONNECT:
            self.on_check_connect()
        elif sig_type == SelfSignal.UPDATE_MONITOR_TIME:
            self.on_update_monitor_time()
        elif sig_type == SelfSignal.ADDRESS_EDIT_CHANGED:
            self.on_address_changed()
        elif sig_type == SelfSignal.PORT_EDIT_CHANGED:
            self.on_port_changed()
        elif sig_type == SelfSignal.FUTURE_SYMBOL_EDIT_CHANGED:
            self.on_future_symbol_changed()
        else:
            pass

    def on_finish_update_orderbook(self, data):
        if not self.update_bid_ask(data):
            return
        self.update_spread_ring()
        if self._checked:
            # print(data)
            self.print_ask_bid_prices()
        buy_spread = self.buy_ring.to_list()
        sell_spread = self.sell_ring.to_list()
        self.buy_spread_line.setData(range(len(buy_spread)), buy_spread)
        self.sell_spread_line.setData(range(len(sell_spread)), sell_spread)

    def on_check_connect(self):
        cur_time = datetime.now()
        # 超时
        if cur_time - self.connect_start_time > timedelta(seconds=5):
            self.qot_ctx.close()
            self.api_status = APIStatus.STOPPED
            self.update_warning_test("连接失败，请检查IP和端口是否正确")
            self.connect_timer.stop()
            self.update_api_status()
            return
        if self.qot_ctx.status == ContextStatus.READY:
            self.api_status = APIStatus.CONNECTED
            self.update_warning_test("连接创建成功，开始监控摆盘")
            self.connect_timer.stop()
            self.update_api_status()
            return

    def on_update_monitor_time(self):
        cur_time = datetime.now()
        used_time = cur_time - self.monitor_start_time
        used_time = timedelta(seconds=int(used_time.total_seconds()))
        self.monitor_used_time_str.setText(str(used_time))

    def on_address_changed(self):
        UtilFuncs.set_addtess_str(self.ip_address_edit.toPlainText())

    def on_port_changed(self):
        UtilFuncs.set_port_str(self.port_edit.toPlainText())

    def on_future_symbol_changed(self):
        UtilFuncs.set_future_symbol_str(self.future_symbol_edit.toPlainText())

    def on_debug_check_box(self):
        self._checked = self.debug_check_box.checkState()

    def start_monitoring(self):
        if self.api_status != APIStatus.CONNECTED:
            self.update_warning_test("当前状态不是已连接，无法开始监控！")
            return
        self.handler = OrderBookCallback(self.on_recv_orderbook)
        self.qot_ctx.set_handler(self.handler)
        front_symbol = self.front_symbol_box.itemText(self.front_symbol_box.currentIndex())
        back_symbol = self.back_symbol_box.itemText(self.back_symbol_box.currentIndex())
        front_symbol = front_symbol[0:front_symbol.find(" ")]
        back_symbol = back_symbol[0:back_symbol.find(" ")]
        ret, data = self.qot_ctx.subscribe([front_symbol, back_symbol], [SubType.ORDER_BOOK])
        if ret != RET_OK:
            self.update_warning_test("Subscribe failed: " + data)
            return
        self.cur_sym = front_symbol
        self.cur_bid = None
        self.cur_ask = None
        self.next_sym = back_symbol
        self.next_bid = None
        self.next_ask = None
        self.buy_ring = Ring(100000)
        self.sell_ring = Ring(100000)
        self.api_status = APIStatus.MONITORING
        self._checked = False
        self.debug_check_box.setChecked(False)

        self.monitor_start_time = datetime.now()
        self.monitor_start_time_str.setText(self.monitor_start_time.strftime("%Y-%m-%d %H:%M:%S"))

        self.start_timer()
        self.update_subscribe_data()
        self.update_api_status()

    def start_timer(self):
        self.info_timer.start(1000)

    def stop_timer(self):
        self.info_timer.stop()

    def closeEvent(self, a0):
        if self.api_status != APIStatus.STOPPED:
            self.qot_ctx.close()

    def update_warning_test(self, warn_text=""):
        self.warning_text.setText(warn_text)
        self.warning_text.update()

    def print_ask_bid_prices(self):
        print("=== {}: {} - {}; \t\t{}: {} - {} ===".format(self.cur_sym, self.cur_ask, self.cur_bid, self.next_sym, self.next_ask, self.next_bid))


def main():
    app = QApplication([])
    window = MyApp()
    window.setFixedSize(1920, 1080)
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
    # test()

