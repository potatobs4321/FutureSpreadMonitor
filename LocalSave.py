from enum import Enum
import os
from Constants import LOCAL_SAVE_FILE_NAME, FILE_ENCODING
from Debouncer import Debouncer


class SaveField(Enum):
    SaveField_IP_Address = 1
    SaveField_Port = 2
    SaveField_Future_Symbol = 3


class LocalSave:
    __save_file_name__ = LOCAL_SAVE_FILE_NAME
    __comma_str__ = ","
    __inited__ = False
    __data_dict__ = {}
    __debouncer__ = None

    @classmethod
    def load_data_from_file(cls):
        if cls.__inited__:
            return
        cls.__inited__ = True
        if os.path.exists(cls.__save_file_name__):
            with open(cls.__save_file_name__, 'r', encoding=FILE_ENCODING) as f:
                for line in f:
                    key, value = cls.parse_line_to_key_value(line)
                    if key is not None:
                        cls.__data_dict__[key] = value

    @classmethod
    def save_data_to_file(cls, _):
        if not cls.__inited__:
            return
        print("save_data_to_file")
        write_line = ""
        for key in cls.__data_dict__:
            value = cls.__data_dict__[key]
            write_line += cls.pack_key_value_to_line_str(key, value)
            write_line += '\n'
        with open(cls.__save_file_name__, 'w', encoding=FILE_ENCODING) as f:
            f.write(write_line)

    @classmethod
    def parse_line_to_key_value(cls, line_str: str):
        line_str = line_str.strip()
        pos = line_str.find(cls.__comma_str__)
        if pos <= 0:
            return None, ""
        key_str = line_str[:pos]
        if not key_str.isdigit():
            return None, ""
        value_str = line_str[pos + 1:]
        return int(key_str), value_str

    @classmethod
    def pack_key_value_to_line_str(cls, key, value):
        try:
            line_str = str(key) + cls.__comma_str__ + str(value)
            return line_str
        except Exception as ex:
            return None

    @classmethod
    def get_value_by_save_field(cls, field: SaveField):
        cls.load_data_from_file()
        if field.value in cls.__data_dict__:
            return cls.__data_dict__[field.value]
        return ""

    @classmethod
    def set_value_by_save_field(cls, field: SaveField, value: str):
        cls.load_data_from_file()
        cls.__data_dict__[field.value] = value
        cls.__debouncer__.trigger()

LocalSave.__debouncer__ = Debouncer(LocalSave.save_data_to_file, 1000)

def main():
    LocalSave.set_value_by_save_field(SaveField.SaveField_Future_Symbol, "HK.HSImain")

    return


if __name__ == '__main__':
    main()

