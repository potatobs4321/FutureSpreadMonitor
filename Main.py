from PyQt5.QtWidgets import *

from WidgetWindows.LoginView import LoginView


def main():
    app = QApplication([])
    login_window = LoginView()
    login_window.show()
    app.exec_()


if __name__ == '__main__':
    main()

