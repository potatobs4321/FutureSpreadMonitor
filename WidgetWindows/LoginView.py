from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QTextEdit, QSpacerItem, QSizePolicy, QVBoxLayout, QPushButton, \
    QApplication

from PyQt5.QtCore import Qt

from FutuAPI.APIContext import ContextMgr
from FutuAPI.FutuAPIContext import FutuAPIContext
from GlobalEvents import GlobalEvents, ID_GlobalEvent_Login_Success, ID_GlobalEvent_Login_Failed
from Util import UtilFuncs
from WidgetWindows.StrategyLabs import StrategyLabMgr


class ItemEdit(QWidget):
    def __init__(self, parent, text, edit_text):
        super().__init__(parent)
        _layout = QHBoxLayout()

        self._text = QLabel(text)
        self._edit = QTextEdit(edit_text)
        self._edit.setFixedSize(150, 30)
        self._edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        _layout.setSpacing(4)
        _layout.addWidget(self._text)
        _layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))
        _layout.addWidget(self._edit)
        _layout.setContentsMargins(0, 0, 0, 0)

        self.setFixedHeight(30)
        self.setLayout(_layout)

    def set_enable(self, enable):
        self._edit.setEnabled(enable)

    def get_edit_test(self):
        return self._edit.toPlainText()


class LoginView(QWidget):

    def __init__(self):
        super().__init__()
        self.setFixedSize(600, 400)
        self.setup_ui()
        self.setup_events()

    def setup_ui(self):
        _layout = QVBoxLayout()

        self._ip_edit = ItemEdit(self, "IP", UtilFuncs.get_address_str())
        self._port_edit = ItemEdit(self, "端口", UtilFuncs.get_port_str())
        self._login_btn = QPushButton("连接")
        self._login_btn.clicked.connect(self.on_login_clicked)
        self._login_btn.setFixedSize(120, 30)
        self._warn_text = QLabel("")
        self._warn_text.setStyleSheet("""
            QLabel {
                color: red;               /* 字体颜色 */
                font-weight: bold;        /* 加粗 */
            }
        """)

        _layout.addWidget(self._ip_edit)
        _layout.addWidget(self._port_edit)
        _layout.addWidget(self._login_btn, alignment=Qt.AlignRight)
        _layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))
        _layout.addWidget(self._warn_text, alignment=Qt.AlignRight)
        _layout.setContentsMargins(50, 50, 50, 50)
        self.setLayout(_layout)

    def setup_events(self):
        GlobalEvents.register_event(ID_GlobalEvent_Login_Success, self.on_login_success)
        GlobalEvents.register_event(ID_GlobalEvent_Login_Failed, self.on_login_failed)

    def on_login_clicked(self):
        _address = self._ip_edit.get_edit_test()
        _port = self._port_edit.get_edit_test()
        print("ip=", _address, ", port=", _port)
        UtilFuncs.set_addtess_str(_address)
        UtilFuncs.set_port_str(_port)
        ContextMgr.init_api_context(FutuAPIContext())
        ContextMgr.init_connect(_address, int(_port))
        self.update_self_status("connecting")

    def on_login_success(self, param):
        StrategyLabMgr.init_lab()
        self.close()

    def on_login_failed(self, param):
        self.show_failed_text()
        self.update_self_status("connect_failed")

    def show_failed_text(self):
        self._warn_text.setText("连接失败")

    def update_self_status(self, status_str):
        if status_str == "connecting":
            self._ip_edit.set_enable(False)
            self._port_edit.set_enable(False)
            self._login_btn.setText("连接中...")
            self._login_btn.setEnabled(False)
        elif status_str == "connect_failed":
            self._ip_edit.set_enable(True)
            self._port_edit.set_enable(True)
            self._login_btn.setText("重新连接")
            self._login_btn.setEnabled(True)


def main():
    app = QApplication([])
    login_window = LoginView()
    login_window.show()
    app.exec_()


if __name__ == '__main__':
    main()
    # test()

