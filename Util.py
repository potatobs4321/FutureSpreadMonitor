import Constants
from Constants import *
from LocalSave import LocalSave, SaveField


class Ring:
    def __init__(self, capacity):
        self._data = [0] * (capacity + 1)
        self._capacity = capacity
        self._begin = 0
        self._end = 0

    def push_back(self, item):
        self._data[self._end] = item
        self._end = (self._end + 1) % (self._capacity + 1)
        if self._end == self._begin:
            self._begin = (self._begin + 1) % (self._capacity + 1)

    def size(self):
        _diff = (self._end + self._capacity - self._begin + 1) % (self._capacity + 1)
        return _diff

    def to_list(self):
        ret_list = []
        for i in range(self.size()):
            ret_list.append(self.__getitem__(i))
        return ret_list

    def __getitem__(self, index):
        return self._data[(self._begin + index) % (self._capacity + 1)]

    def __repr__(self):
        _repr_str = "["
        for i in range(self.size()):
            if i != 0:
                _repr_str += ", "
            _repr_str += str(self.__getitem__(i))
        _repr_str += "]"
        return _repr_str


class UtilFuncs:
    @staticmethod
    def number_to_comma_str(num: int):
        return f"{num:,.0f}"

    @staticmethod
    def is_linked_future_contract(symbol: str):
        key_words_list = [LINKED_CONTRACT_POSTFIX_MAIN, LINKED_CONTRACT_POSTFIX_CURRENT,\
            LINKED_CONTRACT_POSTFIX_NEXT, LINKED_CONTRACT_POSTFIX_DAY]
        for key_word in key_words_list:
            if symbol.find(key_word) > 0:
                return True
        return False

    @staticmethod
    def get_address_str():
        ret_str = LocalSave.get_value_by_save_field(SaveField.SaveField_IP_Address)
        if ret_str == "":
            ret_str = Constants.DEFAULT_ADDRESS
        return ret_str

    @staticmethod
    def set_addtess_str(address):
        LocalSave.set_value_by_save_field(SaveField.SaveField_IP_Address, address)

    @staticmethod
    def get_port_str():
        ret_str = LocalSave.get_value_by_save_field(SaveField.SaveField_Port)
        if ret_str == "":
            ret_str = Constants.DEFAULT_PORT
        return ret_str

    @staticmethod
    def set_port_str(port):
        LocalSave.set_value_by_save_field(SaveField.SaveField_Port, port)

    @staticmethod
    def get_future_symbol_str():
        ret_str = LocalSave.get_value_by_save_field(SaveField.SaveField_Future_Symbol)
        if ret_str == "":
            ret_str = Constants.DEFAULT_FUTURE_SYMBOL
        return ret_str

    @staticmethod
    def set_future_symbol_str(symbol):
        LocalSave.set_value_by_save_field(SaveField.SaveField_Future_Symbol, symbol)


def main():
    # print(UtilFuncs.number_to_comma_str(8039))
    for i in range(10000000):
        LocalSave.set_value_by_save_field(SaveField.SaveField_Future_Symbol, "HK.HSImain")
    return


if __name__ == '__main__':
    main()

