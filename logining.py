import datetime
import os
import sys


class Logining():
    def __init__(self, sys_path: str = "", time_delta_hour: int = 3):
        self.sys_path = sys_path
        self.folder_path = sys_path + "\\logs"
        self.time_delta_hour = time_delta_hour
        self.time_delta = datetime.timedelta(hours=self.time_delta_hour, minutes=0)

    def _getTime(self):
        return datetime.datetime.now(datetime.timezone.utc) + self.time_delta

    def _getDay(self):
        time = self._getTime()
        return str(time.day) + "." + str(time.month) + "." + str(time.year)

    def _getHour(self):
        time = self._getTime()
        return str(time.hour) + "h." + str(time.minute) + "m." + str(time.second) + "s."

    def _writeToLog(self, text):
        try:
            if not os.path.exists(self.folder_path):
                os.makedirs(self.folder_path)
            with open("{0}\\{1}.txt".format(self.folder_path, self._getDay()), 'a', encoding="utf-8") as file:
                file.write("At {0}\n".format(self._getHour()) + text)
        except Exception as E:
            print(sys._getframe().f_code.co_name, E.args)

    def error(self, function_name, error_text):
        info = "    Function: {0}\n    Error:    {1}\n".format(function_name, error_text)
        self._writeToLog(info)

    def userAct(self, function_name, user_id, user_name, text):
        info = "    Function: {0}\n    User:     {1}\n    Id:       {2}\n    Text:     {3}\n".format(function_name, user_name, user_id, text)
        self._writeToLog(info)
