import threading
import time
from PyQt5.QtCore import QTimer


class Task:
    def __init__(self, call_back, interval):
        self._call_back = call_back
        self._interval = interval

    @property
    def call_back(self):
        return self._call_back

    @property
    def interval(self):
        return self._interval


class Debouncer:
    def __init__(self, call_back, interval):
        self._call_back = call_back
        self._interval = interval
        self._timer = QTimer()
        self._timer.timeout.connect(self.execute_task)
        self._parameter = {}
        self._last_trigger_time = 0
        self._active = False

    def trigger(self, parameter=None, execute_immediately=False):
        self._parameter = parameter
        cur_time = self.get_mili_timestamp()
        if execute_immediately and cur_time - self._last_trigger_time > self._interval:
            self.execute_task()
        else:
            if self._active:
                return
            self._active = True
            time_to_wait = self._interval - (cur_time - self._last_trigger_time)
            if time_to_wait < 0 or time_to_wait > self._interval:
                time_to_wait = self._interval
            time_to_wait = int(time_to_wait)
            print(time_to_wait)
            self._timer.start(time_to_wait)

    def execute_task(self):
        print("execute_task")
        self._call_back(self._parameter)
        self._last_trigger_time = self.get_mili_timestamp()
        self._timer.stop()
        self._active = False

    def get_mili_timestamp(self):
        return time.time() * 1000


def main():
    def show_num(num):
        print(num)
    my_debouncer = Debouncer(show_num, 200)
    for i in range(10000000):
        my_debouncer.trigger(i, False)
    return


if __name__ == '__main__':
    threading.Thread(target=main)
    app = QApplication([])
    app.exec_()

