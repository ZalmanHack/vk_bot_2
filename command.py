import datetime
import json
import random

import database
import keyboard
import timetable
import user


class Command():

    def _init_keyboards(self):
        # главное меню -------------------------------------------------------------------------------------------------
        buttons = [[self.keyboards.get_button(label="Сессия", color="primary", payload="Session")],
                   [self.keyboards.get_button(label="Расписание пар", color="default", payload="Couples_sch"),
                    self.keyboards.get_button(label="Расписание звонков", color="default", payload="Call_sch")],
                   [self.keyboards.get_button(label="Тип недели", color="default", payload="Type_of_week")],
                   [self.keyboards.get_button(label="Учебный план", color="default", payload="Academic_plan")],
                   [self.keyboards.get_button(label="Настройки", color="default", payload="Settings")]]
        self.keyboards.addKeyboard(self.KBRD_MENU, False, None, buttons)
        # расписание ---------------------------------------------------------------------------------------------------
        buttons = [[self.keyboards.get_button(label="На сегодня", color="positive", payload="Sch_for_today"),
                    self.keyboards.get_button(label="На завтра", color="primary", payload="Sch_for_tomorrow")],
                   [self.keyboards.get_button(label="На текущую неделю", color="default", payload="Sch_now_week"),
                    self.keyboards.get_button(label="На следующую неделю", color="default", payload="Sch_next_week")],
                   [self.keyboards.get_button(label="Полное расписание", color="default", payload="Full_sch")],
                   [self.keyboards.get_button(label="Главное меню", color="negative", payload="Main_menu")]]
        self.keyboards.addKeyboard(self.KBRD_TIMETABLE, False, None, buttons)
        # учебный план -------------------------------------------------------------------------------------------------
        buttons = [[self.keyboards.get_button(label="1", color="default", payload="Plan_1"),
                    self.keyboards.get_button(label="2", color="default", payload="Plan_2"),
                    self.keyboards.get_button(label="3", color="default", payload="Plan_3"),
                    self.keyboards.get_button(label="4", color="default", payload="Plan_4")],
                   [self.keyboards.get_button(label="5", color="default", payload="Plan_5"),
                    self.keyboards.get_button(label="6", color="default", payload="Plan_6"),
                    self.keyboards.get_button(label="7", color="default", payload="Plan_7"),
                    self.keyboards.get_button(label="8", color="default", payload="Plan_8")],
                   [self.keyboards.get_button(label="Главное меню", color="negative", payload="Main_menu")]]
        self.keyboards.addKeyboard(self.KBRD_ACC_PLAN, False, None, buttons)
        # настройки ----------------------------------------------------------------------------------------------------
        buttons = [
            [self.keyboards.get_button(label="Утренняя рассылка", color="default", payload="Morning_newsletter")],
            [self.keyboards.get_button(label="Вечерняя рассылка", color="default", payload="Evening_newsletter")],
            [self.keyboards.get_button(label="Изменить группу", color="default", payload="Change_group")],
            [self.keyboards.get_button(label="Главное меню", color="negative", payload="Main_menu")]]
        self.keyboards.addKeyboard(self.KBRD_SETTINGS, False, None, buttons)
        # настройки утренней рассылки ----------------------------------------------------------------------------------
        buttons = [[self.keyboards.get_button(label="Включить рассылку", color="positive", payload="On_morning_news")],
                   [self.keyboards.get_button(label="Отключить рассылку", color="default", payload="Off_morning_news")],
                   [self.keyboards.get_button(label="Главное меню", color="negative", payload="Main_menu")]]
        self.keyboards.addKeyboard(self.KBRD_MORNING_M, False, None, buttons)
        # настройки вечерней рассылки ----------------------------------------------------------------------------------
        buttons = [[self.keyboards.get_button(label="Включить рассылку", color="positive", payload="On_evening_news")],
                   [self.keyboards.get_button(label="Отключить рассылку", color="default", payload="Off_evening_news")],
                   [self.keyboards.get_button(label="Главное меню", color="negative", payload="Main_menu")]]
        self.keyboards.addKeyboard(self.KBRD_EVENING_M, False, None, buttons)
        # пустая клавиатура --------------------------------------------------------------------------------------------
        buttons = []
        self.keyboards.addKeyboard(self.KBRD_EMPTY, False, None, buttons)


    def __init__(self, sys_path: str = "", time_delta_hour: int = 3, base_name: str = "Default"):
        # инициализация времени и часового пояса
        self.time_delta_hour = time_delta_hour
        self.time_delta = datetime.timedelta(hours=self.time_delta_hour, minutes=0)
        # инициализация системной папки
        self.sys_path = sys_path
        # виды полей для ответа
        self.ANS_PEER_ID = "peer_id"
        self.ANS_MESSAGE = "message"
        self.AMS_RAND_ID = "random_id"
        self.ANS_KEYBOARD = "keyboard"
        self.ANS_ATTACHMENT = "attachment"
        # виды клавиатур
        self.KBRD_MENU = "menu"
        self.KBRD_TIMETABLE = "timetable"
        self.KBRD_ACC_PLAN = "academic_plan"
        self.KBRD_SETTINGS = "settings"
        self.KBRD_MORNING_M = "morning_mailing"
        self.KBRD_EVENING_M = "evening_mailing"
        self.KBRD_EMPTY = "empty"
        # модуль расписания
        self.timetale = timetable.Timetable(self.sys_path, self.time_delta_hour)
        # модуль клавиатур
        self.keyboards = keyboard.KeyBoard()
        # инициализация клавиатур
        self._init_keyboards()
        # база данных
        self.base_name = base_name
        self.database = database.DataBase(sys_path, self.base_name)

    def mailing(self, group_id=None, time=None):
        if group_id is not None:
            result = []
            table = self.database.get_timetable(group_id)
            users_ids = self.database.get_group_users_ids(group_id)
            for user_id in users_ids:
                answer_morning = self._mailing_tb_morning(user_id, table, time)
                answer_evening = self._mailing_tb_evening(user_id, table, time)
                if answer_morning is not None:
                    result.append(answer_morning)
                if answer_evening is not None:
                    result.append(answer_evening)
            if result:
                return result

    def _mailing_tb_morning(self, user_id=None, table=None, time=None):  # GOOD
        # утренняя рассылка
        if user_id is not None and table is not None:
            if self.database.get_morning_m(user_id):
                message = self.timetale.get_schedule_now(table, time)
                if message is not None:
                    return {self.ANS_MESSAGE: message,
                            self.AMS_RAND_ID: random.randint(1, 2147483647),
                            self.ANS_PEER_ID: user_id}

    def _mailing_tb_evening(self, user_id=None, table=None, time=None):  # GOOD
        # вечерняя рассылка
        if user_id is not None and table is not None:
            if self.database.get_evening_m(user_id):
                if "{0}:{1}".format(time.hour, time.minute) == "18:00":
                    message = self.timetale.get_tomorrow(table)
                    if message is not None:
                        return {self.ANS_MESSAGE: message,
                                self.AMS_RAND_ID: random.randint(1, 2147483647),
                                self.ANS_PEER_ID: user_id}

    def message(self, user_id: int = 0, first_name: str = "No name", second_name: str = "No name", message: dict = ()):
        # класс работы с метаданными пользователя (по id)
        user_meta = user.User(user_id, first_name, second_name)
        # проверка наличия студента в бд
        if not self.database.load_user(user_id):
            return self._registration_user(user_meta, message)
        else:
            # обработка входящего сообщения и получение ответа
            response = self._menus_processing(user_meta, message)
            # дополнение ответа
            response = self._complement_response(user_meta, response)
            return response

    def _registration_user(self, user_meta: user.User, message: dict = ()):
        group_id = self.database.get_group_id(group_name=message["text"])
        if self.database.init_user(user_id=user_meta.user_id, group_id=group_id):
            return {self.ANS_MESSAGE: "{0}, Вы успешно зарегистрированы в группе {1}.\n"
                                      "Вот, что я могу:".format(user_meta.first_name, message["text"]),
                    self.ANS_KEYBOARD: self.keyboards.getKeyboard(self.KBRD_MENU),
                    self.ANS_PEER_ID: user_meta.user_id,
                    self.AMS_RAND_ID: random.randint(1, 2147483647)}
        groups_names = "\n".join(self.database.get_groups_names())
        return {self.ANS_MESSAGE: "{0}, введите название вашей группы.\n"
                                  "Вот список групп:\n{1}".format(user_meta.first_name, groups_names),
                self.ANS_KEYBOARD: self.keyboards.getKeyboard(self.KBRD_EMPTY),
                self.ANS_PEER_ID: user_meta.user_id,
                self.AMS_RAND_ID: random.randint(1, 2147483647)}

    def _menus_processing(self, user_meta: user.User, message: dict = ()):
        # получаем последнюю команду (в файл записываются только те, что имеют контекст, например открытое меню)
        end_command = self.database.get_user_end_command(user_meta.user_id)
        # проверяем последние действия пользователя с  контекстом
        if end_command == self.KBRD_TIMETABLE:  # если последнее действие - открытие меню расписания
            return self._menu_timetable(user_meta, message)
        elif end_command == self.KBRD_ACC_PLAN:  # если последнее действие - открытие меню академ планов
            return self._menu_acc_plan(user_meta, message)
        elif end_command == self.KBRD_SETTINGS:  # если последнее действие - открытие меню настроек рассылки
            return self._menu_settings(user_meta, message)
        elif end_command == self.KBRD_MORNING_M:  # если последнее действие - открытие меню настроек утр. рассылки
            return self._menu_morning_m(user_meta, message)
        elif end_command == self.KBRD_EVENING_M:  # если последнее действие - открытие меню настроек веч. рассылки
            return self._menu_evening_m(user_meta, message)
        else:  # если последнее действие - пустота
            return self._menu_main(user_meta, message)

    def _complement_response(self, user_meta: user.User, response=None):
        if response is None:
            response: dict = {}
            self.database.write_user_end_command(user_meta.user_id, "")
            response[self.ANS_MESSAGE] = "{0}, вот, что я могу:".format(user_meta.first_name)
            response[self.ANS_KEYBOARD] = self.keyboards.getKeyboard(self.KBRD_MENU)
            response[self.ANS_PEER_ID] = user_meta.user_id
            response[self.AMS_RAND_ID] = random.randint(1, 2147483647)
        return response

    def _menu_main(self, user_meta: user.User, message: dict = ()):
        try:
            payload = json.loads(message["payload"])["button"]
            if "Couples_sch" == payload:
                self.database.write_user_end_command(user_meta.user_id, self.KBRD_TIMETABLE)
                return {self.ANS_MESSAGE: "{0}, выбери один из вариантов:".format(user_meta.first_name),
                        self.ANS_KEYBOARD: self.keyboards.getKeyboard(self.KBRD_TIMETABLE),
                        self.ANS_PEER_ID: user_meta.user_id,
                        self.AMS_RAND_ID: random.randint(1, 2147483647)}
            if "Call_sch" == payload:
                return {self.ANS_MESSAGE: self.timetale.get_call_timetable(),
                        self.ANS_KEYBOARD: self.keyboards.getKeyboard(self.KBRD_MENU),
                        self.ANS_PEER_ID: user_meta.user_id,
                        self.AMS_RAND_ID: random.randint(1, 2147483647)}
            if "Type_of_week" == payload:
                return {self.ANS_MESSAGE: "Сейчас " + self.timetale.get_week_type("now") + " неделя",
                        self.ANS_KEYBOARD: self.keyboards.getKeyboard(self.KBRD_MENU),
                        self.ANS_PEER_ID: user_meta.user_id,
                        self.AMS_RAND_ID: random.randint(1, 2147483647)}
            if "Academic_plan" == payload:
                self.database.write_user_end_command(user_meta.user_id, self.KBRD_ACC_PLAN)
                return {self.ANS_MESSAGE: "{0}, выбери один из вариантов:".format(user_meta.first_name),
                        self.ANS_KEYBOARD: self.keyboards.getKeyboard(self.KBRD_ACC_PLAN),
                        self.ANS_PEER_ID: user_meta.user_id,
                        self.AMS_RAND_ID: random.randint(1, 2147483647)}
            if "Settings" == payload:
                self.database.write_user_end_command(user_meta.user_id, self.KBRD_SETTINGS)
                return {self.ANS_MESSAGE: "{0}, выбери один из вариантов:".format(user_meta.first_name),
                        self.ANS_KEYBOARD: self.keyboards.getKeyboard(self.KBRD_SETTINGS),
                        self.ANS_PEER_ID: user_meta.user_id,
                        self.AMS_RAND_ID: random.randint(1, 2147483647)}
        except Exception as e:
            return

    def _menu_timetable(self, user_meta: user.User, message: dict = ()):
        try:
            payload = json.loads(message["payload"])["button"]
            group_id = self.database.get_group_id(user_id=user_meta.user_id)
            table = self.database.get_timetable(group_id)
            if "Sch_for_today" == payload:
                info = self.timetale.get_today(table)
                if info is None:
                    info = "Сегодня пар нет"
                return {self.ANS_MESSAGE: info,
                        self.ANS_KEYBOARD: self.keyboards.getKeyboard(self.KBRD_TIMETABLE),
                        self.ANS_PEER_ID: user_meta.user_id,
                        self.AMS_RAND_ID: random.randint(1, 2147483647)}
            if "Sch_for_tomorrow" == payload:
                info = self.timetale.get_tomorrow(table)
                if info is None:
                    info = "Завтра пар нет"
                return {self.ANS_MESSAGE: info,
                        self.ANS_KEYBOARD: self.keyboards.getKeyboard(self.KBRD_TIMETABLE),
                        self.ANS_PEER_ID: user_meta.user_id,
                        self.AMS_RAND_ID: random.randint(1, 2147483647)}
            if "Sch_now_week" == payload:
                return {self.ANS_MESSAGE: self.timetale.get_week(table, "now"),
                        self.ANS_KEYBOARD: self.keyboards.getKeyboard(self.KBRD_TIMETABLE),
                        self.ANS_PEER_ID: user_meta.user_id,
                        self.AMS_RAND_ID: random.randint(1, 2147483647)}
            if "Sch_next_week" == payload:
                return {self.ANS_MESSAGE: self.timetale.get_week(table, "next"),
                        self.ANS_KEYBOARD: self.keyboards.getKeyboard(self.KBRD_TIMETABLE),
                        self.ANS_PEER_ID: user_meta.user_id,
                        self.AMS_RAND_ID: random.randint(1, 2147483647)}
            if "Full_sch" == payload:
                return {self.ANS_MESSAGE: self.timetale.get_all(table),
                        self.ANS_KEYBOARD: self.keyboards.getKeyboard(self.KBRD_TIMETABLE),
                        self.ANS_PEER_ID: user_meta.user_id,
                        self.AMS_RAND_ID: random.randint(1, 2147483647)}
            if "Main_menu" == payload:
                self.database.write_user_end_command(user_meta.user_id, "")
                return {self.ANS_MESSAGE: "{0}, выбери один из вариантов:".format(user_meta.first_name),
                        self.ANS_KEYBOARD: self.keyboards.getKeyboard(self.KBRD_MENU),
                        self.ANS_PEER_ID: user_meta.user_id,
                        self.AMS_RAND_ID: random.randint(1, 2147483647)}
        except Exception as e:
            return

    def _menu_acc_plan(self, user_meta: user.User, message: dict = ()):
        try:
            payload = json.loads(message["payload"])["button"]
            if "Main_menu" == payload:
                self.database.write_user_end_command(user_meta.user_id, "")
                return {self.ANS_MESSAGE: "{0}, выбери один из вариантов:".format(user_meta.first_name),
                        self.ANS_KEYBOARD: self.keyboards.getKeyboard(self.KBRD_MENU),
                        self.ANS_PEER_ID: user_meta.user_id,
                        self.AMS_RAND_ID: random.randint(1, 2147483647)}
            temp = payload.split("_")
            if len(temp) == 2 and temp[0] == "Plan":
                self.database.write_user_end_command(user_meta.user_id, self.KBRD_ACC_PLAN)
                return {self.ANS_KEYBOARD: self.keyboards.getKeyboard(self.KBRD_ACC_PLAN),
                        self.ANS_ATTACHMENT: {
                            "file_path": "{0}\\academic_plan\\{1}.xlsx".format(self.sys_path, temp[1]),
                            "file_name": "учебный план на {0} семестр.xlsx".format(temp[1])},
                        self.ANS_PEER_ID: user_meta.user_id,
                        self.AMS_RAND_ID: random.randint(1, 2147483647)}
        except Exception as e:
            return

    def _menu_settings(self, user_meta: user.User, message: dict = ()):
        try:
            payload = json.loads(message["payload"])["button"]
            if "Morning_newsletter" == payload:
                self.database.write_user_end_command(user_meta.user_id, self.KBRD_MORNING_M)
                return {self.ANS_MESSAGE: "{0}, выбери один из вариантов:".format(user_meta.first_name),
                        self.ANS_KEYBOARD: self.keyboards.getKeyboard(self.KBRD_MORNING_M),
                        self.ANS_PEER_ID: user_meta.user_id,
                        self.AMS_RAND_ID: random.randint(1, 2147483647)}
            if "Evening_newsletter" == payload:
                self.database.write_user_end_command(user_meta.user_id, self.KBRD_EVENING_M)
                return {self.ANS_MESSAGE: "{0}, выбери один из вариантов:".format(user_meta.first_name),
                        self.ANS_KEYBOARD: self.keyboards.getKeyboard(self.KBRD_EVENING_M),
                        self.ANS_PEER_ID: user_meta.user_id,
                        self.AMS_RAND_ID: random.randint(1, 2147483647)}
            if "Change_group" == payload:
                self.database.delete_user(user_meta.user_id)
                groups_names = "\n".join(self.database.get_groups_names())
                return {self.ANS_MESSAGE: "{0}, введите название вашей группы.\n"
                                          "Вот список групп:\n{1}".format(user_meta.first_name, groups_names),
                        self.ANS_KEYBOARD: self.keyboards.getKeyboard(self.KBRD_EMPTY),
                        self.ANS_PEER_ID: user_meta.user_id,
                        self.AMS_RAND_ID: random.randint(1, 2147483647)}
            if "Main_menu" == payload:
                self.database.write_user_end_command(user_meta.user_id, "")
                return {self.ANS_MESSAGE: "{0}, выбери один из вариантов:".format(user_meta.first_name),
                        self.ANS_KEYBOARD: self.keyboards.getKeyboard(self.KBRD_MENU),
                        self.ANS_PEER_ID: user_meta.user_id,
                        self.AMS_RAND_ID: random.randint(1, 2147483647)}
        except Exception as e:
            return

    def _menu_morning_m(self, user_meta: user.User, message: dict = ()):
        try:
            payload = json.loads(message["payload"])["button"]
            if "On_morning_news" == payload:
                self.database.write_user_end_command(user_meta.user_id, "")
                self.database.write_user_morning_m(user_meta.user_id, True)
                return {self.ANS_MESSAGE: "{0}, утренняя рассылка включена".format(user_meta.first_name),
                        self.ANS_KEYBOARD: self.keyboards.getKeyboard(self.KBRD_MENU),
                        self.ANS_PEER_ID: user_meta.user_id,
                        self.AMS_RAND_ID: random.randint(1, 2147483647)}
            if "Off_morning_news" == payload:
                self.database.write_user_end_command(user_meta.user_id, "")
                self.database.write_user_morning_m(user_meta.user_id, False)
                return {self.ANS_MESSAGE: "{0}, утренняя рассылка отключена".format(user_meta.first_name),
                        self.ANS_KEYBOARD: self.keyboards.getKeyboard(self.KBRD_MENU),
                        self.ANS_PEER_ID: user_meta.user_id,
                        self.AMS_RAND_ID: random.randint(1, 2147483647)}
            if "Main_menu" == payload:
                self.database.write_user_end_command(user_meta.user_id, "")
                return {self.ANS_MESSAGE: "{0}, выбери один из вариантов:".format(user_meta.first_name),
                        self.ANS_KEYBOARD: self.keyboards.getKeyboard(self.KBRD_MENU),
                        self.ANS_PEER_ID: user_meta.user_id,
                        self.AMS_RAND_ID: random.randint(1, 2147483647)}
        except Exception as e:
            return

    def _menu_evening_m(self, user_meta: user.User, message: dict = ()):
        try:
            payload = json.loads(message["payload"])["button"]
            if "On_evening_news" == payload:
                self.database.write_user_end_command(user_meta.user_id, "")
                self.database.write_user_evening_m(user_meta.user_id, True)
                return {self.ANS_MESSAGE: "{0}, вечерняя рассылка включена".format(user_meta.first_name),
                        self.ANS_KEYBOARD: self.keyboards.getKeyboard(self.KBRD_MENU),
                        self.ANS_PEER_ID: user_meta.user_id,
                        self.AMS_RAND_ID: random.randint(1, 2147483647)}
            if "Off_evening_news" == payload:
                self.database.write_user_end_command(user_meta.user_id, "")
                self.database.write_user_evening_m(user_meta.user_id, False)
                return {self.ANS_MESSAGE: "{0}, вечерняя рассылка отключена".format(user_meta.first_name),
                        self.ANS_KEYBOARD: self.keyboards.getKeyboard(self.KBRD_MENU),
                        self.ANS_PEER_ID: user_meta.user_id,
                        self.AMS_RAND_ID: random.randint(1, 2147483647)}
            if "Main_menu" == payload:
                self.database.write_user_end_command(user_meta.user_id, "")
                return {self.ANS_MESSAGE: "{0}, выбери один из вариантов:".format(user_meta.first_name),
                        self.ANS_KEYBOARD: self.keyboards.getKeyboard(self.KBRD_MENU),
                        self.ANS_PEER_ID: user_meta.user_id,
                        self.AMS_RAND_ID: random.randint(1, 2147483647)}
        except Exception as e:
            return


if __name__ == "__main__":
    com = Command(sys_path="test_commands")
    print(com.message(778, "Денис", "Добренко", {"payload": "{\"button\": \"" + str("Academic_plan") + "\"}"}))
    print(com.message(778, "Денис", "Добренко", {"payload": "{\"button\": \"" + str("Plan_1") + "\"}"}))
