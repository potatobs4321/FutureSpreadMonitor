from futu import *


class OrderBookCallback(OrderBookHandlerBase):
    def __init__(self, _call_back):
        super(OrderBookCallback, self).__init__()
        self.call_back = _call_back

    def on_recv_rsp(self, rsp_pb):
        ret_code, data = super(OrderBookCallback,self).on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            print("OrderBookTest: error, msg: %s" % data)
            return RET_ERROR, data
        if self.call_back is not None:
            self.call_back(data)
        return RET_OK, data


def main():
    pass


if __name__ == '__main__':
    main()

