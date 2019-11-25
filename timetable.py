import datetime
import json
import os


class Timetable():
    def __init__(self, sys_path: str = "",  time_delta_hour: int = 3):
        # часовой пояс
        self.time_delta_hour = time_delta_hour
        self.time_delta = datetime.timedelta(hours=self.time_delta_hour, minutes=0)
        # папка класса
        self.folder_path = sys_path + "\\" + "timetable"
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)
        # получение расписания
        self.call_timetable = self._open_file_json("call_timetable")

    def _open_file_json(self, name):
        try:
            file_timetable = open('{0}\\{1}.json'.format(self.folder_path, name), 'r', encoding="utf-8")
            return json.load(file_timetable)
        except Exception as E:
            return {}

    def _get_schedule(self, num_schedule, data_schedule):
        # расписание {1 : 8:00, 2 : 9:55..}
        scheduled_num = {b: a for a, b in self.call_timetable.items()}
        result = "{0}\n{1} {2}\n{3}\n".format(
            data_schedule["discipline"], data_schedule["class"], data_schedule["type"], data_schedule["teacher"])
        if len(result) != 0:
            return "❗ {0} ❗ {1} ❗\n".format(num_schedule, scheduled_num[num_schedule]) + result
        return ""

    def _get_day(self, name_day, data_day):
        week_days = {
            "1": "понедельник",
            "2": "вторник",
            "3": "среда",
            "4": "четверг",
            "5": "пятница",
            "6": "суббота",
            "7": "воскресение"
        }
        result = ""
        for time_schedule, data_schedule in data_day.items():
            result += self._get_schedule(time_schedule, data_schedule)
        if len(result) != 0:
            return "◾◾ {0} ◾◾\n".format(week_days[name_day]) + result
        return ""

    def _get_week(self, week_type, data_week):
        week_types = {
            "top": "верхняя",
            "lower": "нижняя"
        }
        result = ""
        for name_day, data_day in data_week.items():
            result += self._get_day(name_day, data_day)
        if len(result) != 0:
            return "✅ {0} ✅\n".format(week_types[week_type]) + result

    def _get_weeks(self, data):
        result = ""
        for week_num, data_week in data.items():
            result += self._get_week(week_num, data_week)
        return result

    def _get_week_type(self, type: str = "now"):
        try:
            param = 0
            if type == "next":
                param = 1
            time = datetime.datetime.now(datetime.timezone.utc) + self.time_delta
            if int(time.strftime("%W")) % 2 == param:
                return {"rus": "нижняя", "eng": "lower"}
            else:
                return {"rus": "верхняя", "eng": "top"}
        except Exception as e:
            return {}

    # ------------------------------------------------------------------------------------------------------------------

    def get_week_type(self, type: str = "now"):
        return self._get_week_type(type)["rus"]

    def get_week(self, timetable=None, type: str = "now"):
        try:
            if timetable is not None:
                week_type = self._get_week_type(type)["eng"]
                data_week = timetable[self._get_week_type(type)["eng"]]
                result = self._get_week(week_type, data_week)
                if len(result) != 0:
                    return result
        except Exception as e:
            return

    def get_day(self, timetable=None, day: str = "1"):
        try:
            if timetable is not None:
                if day in timetable[self._get_week_type('now')["eng"]]:
                    data_day = timetable[self._get_week_type('now')["eng"]][day]
                    result = self._get_day(day, data_day)
                    if len(result) != 0:
                        return result
        except Exception as e:
            return

    def get_today(self, timetable=None):
        if timetable is not None:
            time = datetime.datetime.now(datetime.timezone.utc) + self.time_delta
            day = time.weekday() + 1  # + 1 чтобы было от 1 до 7
            return self.get_day(timetable, str(day))

    def get_tomorrow(self, timetable=None):
        if timetable is not None:
            time = datetime.datetime.now(datetime.timezone.utc) + self.time_delta
            day = time.weekday() + 2  # + 1 чтобы было от 1 до 7 и + 1 для завтра
            if day > 7:
                day = 1
            return self.get_day(timetable, str(day))

    def get_all(self, timetable=None):
        try:
            if timetable is not None:
                result = self._get_weeks(timetable)
                if len(result) != 0:
                    return result
        except Exception as e:
            return "Произошла ошибка"

    def get_schedule(self, timetable=None, type: str = "now", day: str = "1", schedule: str = "1"):
        try:
            if timetable is not None:
                if day in timetable[self._get_week_type(type)["eng"]]:
                    if schedule in timetable[self._get_week_type(type)["eng"]][day]:
                        data_schedule = timetable[self._get_week_type(type)["eng"]][day][schedule]
                        result = self._get_schedule(schedule, data_schedule)
                        if len(result) != 0:
                            return result
        except Exception as e:
            return "Произошла ошибка"

    def get_schedule_now(self, timetable=None, time=None): # GOOD
        try:
            if timetable is not None:
                if time is None:
                    time = datetime.datetime.now(datetime.timezone.utc) + self.time_delta
                type = self._get_week_type("now")["eng"]
                day = str(time.weekday() + 1)  # от 0 до 6
                schedule = "{0}:{1}".format(time.hour, time.minute)
                if schedule not in self.call_timetable:
                    return
                if day not in timetable[self._get_week_type(type)["eng"]]:
                    return
                if self.call_timetable[schedule] not in timetable[self._get_week_type(type)["eng"]][day]:
                    return
                data_schedule = timetable[self._get_week_type(type)["eng"]][day][self.call_timetable[schedule]]
                result = self._get_schedule(self.call_timetable[schedule], data_schedule)
                if len(result) != 0:
                    return result
        except Exception as e:
            return

    def get_call_timetable(self):
        try:
            result = ""
            for time, num in self.call_timetable.items():
                result += "{0} ❗ {1}\n".format(num, time)
            if len(result) != 0:
                return "Расписание звонков:\n" + result
        except Exception as e:
            return "Произошла ошибка"
        return ""


if __name__ == "__main__":
    test = Timetable()
    print(test.get_tomorrow())
