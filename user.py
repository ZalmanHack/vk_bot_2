import json
import os
import sys


class User():
    def __init__(self, user_id: int = 0, first_name: str = "No name", second_name: str = "No name"):
        self.user_id = user_id
        self.first_name = first_name
        self.second_name = second_name

    """
    def __init__(self, sys_path: str = "", user_id: int = 0, first_name: str = "No name", second_name: str = "No name"):
        self.user_id = user_id

        self.first_name = first_name
        self.second_name = second_name
        # создаем папку
        self.sys_path = sys_path
        self.folder_path = sys_path + "\\" + "users_data"
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)
        #
        self.file_name = "users"
        self._init_in_file()

    def _init_in_file(self):
        json_file = self._open()
        if str(self.user_id) not in json_file:
            json_file[str(self.user_id)] = {}
            self._write(json_file)

    def _open(self):
        try:
            if not os.path.exists(self.folder_path):
                os.makedirs(self.folder_path)
            file = open("{0}\\{1}.json".format(self.folder_path, self.file_name), 'r', encoding="utf-8")
            result = json.load(file)
            file.close()
            return result
        except IOError as e:  # если файл не нашли
            return self._write()
        except Exception as E:
            print(sys._getframe().f_code.co_name, E.args)

    def _write(self, data=None):
        if data is None:
            data = {}
        file = open("{0}\\{1}.json".format(self.folder_path, self.file_name), 'w', encoding="utf-8")
        json.dump(data, file, indent=4, ensure_ascii=False)
        file.close()
        return data


    def add(self, key: str = "", data=None):
        if data is None:
            data = ""
        json_file = self._open()
        if str(self.user_id) not in json_file:
            json_file[str(self.user_id)] = {}
        json_file[str(self.user_id)][key] = data
        self._write(json_file)

    def get(self, key):
        json_file = self._open()
        if str(self.user_id) in json_file:
            if key in json_file[str(self.user_id)]:
                return json_file[str(self.user_id)][key]
        return None


    def get_first_name(self):
        return self.first_name

    def get_second_name(self):
        return self.second_name
"""

if __name__ == "__main__":
    test = User()
    print(test.get("ДД2"))
