from PyQt5.QtCore import pyqtSignal, QObject

ID_GlobalEvent_Min = 10000
ID_GlobalEvent_Login_Success = ID_GlobalEvent_Min + 1
ID_GlobalEvent_Login_Failed = ID_GlobalEvent_Min + 2
ID_GlobalEvent_App_Exit = ID_GlobalEvent_Min + 3
ID_GlobalEvent_Max = 1000000


class GlobalEventEmitter(QObject):
    """实际持有信号的对象"""
    event_signal = pyqtSignal(int, dict)  # 信号定义必须在QObject子类中


class GlobalEvents:
    _self_emiter = GlobalEventEmitter()
    _events = {}
    _connected = False

    @classmethod
    def register_event(cls, event_id: int, callback):
        if event_id < ID_GlobalEvent_Min or event_id > ID_GlobalEvent_Max:
            print("invalid event id!")
            return
        """注册事件回调"""
        if not cls._connected:
            cls._self_emiter.event_signal.connect(cls.execute_callbacks)
            cls._connected = True
        if event_id not in cls._events:
            cls._events[event_id] = []
        if callback not in cls._events[event_id]:
            cls._events[event_id].append(callback)

    @classmethod
    def notify_event(cls, event_id, params={}):
        """发信号，放到主线程中执行回调"""
        cls._self_emiter.event_signal.emit(event_id, params)

    @classmethod
    def execute_callbacks(cls, event_id, params):
        """触发事件，执行所有回调"""
        if event_id in cls._events:
            for callback in cls._events[event_id]:
                callback(params)

    @classmethod
    def remove_event(cls, event_id, callback=None):
        """移除事件回调（如果未指定callback，则移除整个事件）"""
        if event_id in cls._events:
            if callback is None:
                cls._events.pop(event_id)
            else:
                cls._events[event_id] = [cb for cb in cls._events[event_id] if cb != callback]