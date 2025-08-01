from PyQt5.QtCore import pyqtSignal, QTimer
from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout

from GlobalEvents import GlobalEvents, ID_GlobalEvent_App_Exit
from WidgetWindows.FutureSpreadWidget import FutureSpreadWidget
from PyQt5.QtWidgets import *

class StrategyLabs(QWidget):
    _signals_ = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        print("StrategyLabs.__init__")
        _layout = QVBoxLayout()
        self._tab_widget = QTabWidget()

        self._future_spread = FutureSpreadWidget()
        self._empty = QWidget()

        self._tab_widget.addTab(self._empty, "空白")
        self._tab_widget.addTab(self._future_spread, "期货价差")

        _layout.addWidget(self._tab_widget)
        self.setMinimumSize(800, 600)
        self.setLayout(_layout)

    def closeEvent(self, a0):
        GlobalEvents.notify_event(ID_GlobalEvent_App_Exit)


class StrategyLabMgr:
    _impl_ = None
    @classmethod
    def init_lab(cls):
        cls._impl_ = StrategyLabs()
        cls._impl_.show()


def main():
    app = QApplication([])
    login_window = StrategyLabs()
    login_window.show()
    app.exec_()


if __name__ == '__main__':
    main()
    # test()

