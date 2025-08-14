
from datetime import datetime, timedelta

from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt5.QtWidgets import *
import pyqtgraph as pg
from enum import Enum

from futu import *
from Util import Ring, UtilFuncs
from Callbacks import OrderBookCallback
from Constants import *
from WidgetWindows.StrategyTabs.FutureSpreadModel import FutureSpreadModel, FutureSpreadSignal, MonitorStatus


class SelfSignal(Enum):
    UPDATE_ORDERBOOK = "UPDATE_ORDERBOOK"
    CHECK_CONNECT = "CHECK_CONNECT"
    UPDATE_MONITOR_TIME = "UPDATE_MONITOR_TIME"
    ADDRESS_EDIT_CHANGED = "ADDRESS_EDIT_CHANGED"
    PORT_EDIT_CHANGED = "PORT_EDIT_CHANGED"
    FUTURE_SYMBOL_EDIT_CHANGED = "FUTURE_SYMBOL_EDIT_CHANGED"


class FutureSpreadWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_model()
        self.setup_ui()

    def setup_model(self):
        self._model = FutureSpreadModel()
        self._model._model_signal.connect(self.on_recv_model_signal)

    def setup_ui(self):
        self.setMinimumSize(800, 600)

        # self.sub_status = QWidget(self)
        # sub_status_layout = QHBoxLayout()
        # self.api_status_text = QLabel("当前状态：")
        # self.total_sub_text = QLabel("    总订阅额度：")
        # self.total_sub_num = QLabel("--")
        # self.remain_sub_text = QLabel("    剩余订阅额度：")
        # self.remain_sub_num = QLabel("--")
        # self.monitor_start_time_text = QLabel("    监控开始时间：")
        # self.monitor_start_time_str = QLabel("--")
        # self.monitor_used_time_text = QLabel("    已监控：")
        # self.monitor_used_time_str = QLabel("--")
        # sub_status_layout.addWidget(self.api_status_text)
        # sub_status_layout.addWidget(self.total_sub_text)
        # sub_status_layout.addWidget(self.total_sub_num)
        # sub_status_layout.addWidget(self.remain_sub_text)
        # sub_status_layout.addWidget(self.remain_sub_num)
        # sub_status_layout.addWidget(self.monitor_start_time_text)
        # sub_status_layout.addWidget(self.monitor_start_time_str)
        # sub_status_layout.addWidget(self.monitor_used_time_text)
        # sub_status_layout.addWidget(self.monitor_used_time_str)
        # sub_status_layout.setSpacing(8)
        # sub_status_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))
        # self.sub_status.setLayout(sub_status_layout)

        self.interaction_edit = QWidget(self)
        interaction_edit_layout = QHBoxLayout()
        self.future_symbol_text = QLabel("期货合约：")
        self.front_symbol_text = QLabel("近月合约：")
        self.back_symbol_text = QLabel("远月合约：")
        self.update_combobox_btn = QPushButton("获取所有合约")
        self.update_combobox_btn.clicked.connect(self.pull_future_list)
        self.future_symbol_edit = QTextEdit()
        self.future_symbol_edit.setFixedSize(150, 30)
        self.future_symbol_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.future_symbol_edit.setText(UtilFuncs.get_future_symbol_str())
        self.future_symbol_edit.textChanged.connect(self.on_future_symbol_changed)
        self.front_symbol_box = QComboBox()
        self.front_symbol_box.setFixedSize(150, 30)
        self.front_symbol_box.currentIndexChanged.connect(self.on_front_combobox_selected)
        self.back_symbol_box = QComboBox()
        self.back_symbol_box.setFixedSize(150, 30)
        self.back_symbol_box.currentIndexChanged.connect(self.on_back_combobox_selected)
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
        self.monitor_btn = QPushButton("开始监听")
        self.monitor_btn.clicked.connect(self.on_monitor_button_clicked)
        self.debug_check_box = QCheckBox("控制台输出摆盘价格")
        self.debug_check_box.clicked.connect(self.on_debug_check_box)
        self.api_status_enum = QLabel("--")
        interaction_btn_layout.addWidget(self.monitor_btn)
        interaction_btn_layout.addWidget(self.debug_check_box)
        interaction_btn_layout.setSpacing(8)
        interaction_btn_layout.setContentsMargins(0, 0, 0, 0)
        interaction_btn_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))
        interaction_btn_layout.addWidget(self.api_status_enum)
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
        # layout.addWidget(self.sub_status)
        layout.addWidget(self.interaction_edit)
        layout.addWidget(self.interaction_btn)
        layout.addWidget(self.plot_widget, 0)
        self.setLayout(layout)

        self.update_api_status(self._model.get_status())

    def update_api_status(self, status):
        status_dict = {
            MonitorStatus.Stopped: "未监控",
            MonitorStatus.Monitoring: "监听中",
        }
        self.api_status_enum.setText(status_dict[status])
        if status == MonitorStatus.Stopped:
            self.monitor_btn.setText("开始监听")
            self.update_combobox_btn.setEnabled(True)
            self.front_symbol_box.setEnabled(True)
            self.back_symbol_box.setEnabled(True)
        elif status == MonitorStatus.Monitoring:
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

    def on_monitor_button_clicked(self):
        model_status = self._model.get_status()
        if model_status == MonitorStatus.Stopped:
            self._model.start_monitor()
        elif model_status == MonitorStatus.Monitoring:
            self._model.stop_monitor()

    def on_front_combobox_selected(self, index):
        symbol_text = self.front_symbol_box.itemText(index)
        symbol_str = symbol_text[0:symbol_text.find(" ")]
        self._model.set_current_symbol(symbol_str)

    def on_back_combobox_selected(self, index):
        symbol_text = self.back_symbol_box.itemText(index)
        symbol_str = symbol_text[0:symbol_text.find(" ")]
        self._model.set_next_symbol(symbol_str)

    def on_recv_model_signal(self, signal):
        if signal == FutureSpreadSignal.StatusChanged:
            self.update_api_status(self._model.get_status())
        elif signal == FutureSpreadSignal.OrderBookUpdate:
            self.on_finish_update_orderbook()
        elif signal == FutureSpreadSignal.FinishPullFutureList:
            self.on_finish_pull_future_list()

    def pull_future_list(self):
        self._model.pull_future_list()

    def on_finish_pull_future_list(self):
        future_list = self._model.get_future_related_symbols()
        print(future_list)
        self.front_symbol_box.clear()
        self.back_symbol_box.clear()
        for item in future_list:
            item_str = "{}  ({})".format(item.sym, UtilFuncs.number_to_comma_str(item.vol))
            self.front_symbol_box.addItem(item_str)
            self.back_symbol_box.addItem(item_str)

        font_metrics = self.front_symbol_box.fontMetrics()
        max_width = max(font_metrics.width(text) for text in
                        [self.front_symbol_box.itemText(i) for i in range(self.front_symbol_box.count())])

        # 设置下拉菜单的最小宽度（额外加一些 padding）
        self.front_symbol_box.view().setMinimumWidth(max_width + 40)
        self.back_symbol_box.view().setMinimumWidth(max_width + 40)

    def on_finish_update_orderbook(self):
        buy_spread = self._model.get_buy_spread_list()
        sell_spread = self._model.get_sell_spread_list()
        self.buy_spread_line.setData(range(len(buy_spread)), buy_spread)
        self.sell_spread_line.setData(range(len(sell_spread)), sell_spread)

    def on_update_monitor_time(self):
        cur_time = datetime.now()
        used_time = cur_time - self.monitor_start_time
        used_time = timedelta(seconds=int(used_time.total_seconds()))
        self.monitor_used_time_str.setText(str(used_time))

    def on_future_symbol_changed(self):
        self._model.set_future_base_symbol(self.future_symbol_edit.toPlainText())

    def on_debug_check_box(self):
        self._model.set_checked(self.debug_check_box.checkState())

    def start_timer(self):
        self.info_timer.start(1000)

    def stop_timer(self):
        self.info_timer.stop()

    def closeEvent(self, event):
        self._model.close()
