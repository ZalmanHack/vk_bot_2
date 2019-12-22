from command import *
import user

class Command_headman(Command):
    def __init__(self, sys_path: str = "", time_delta_hour: int = 3, base_name: str = "Default"):
        Command.__init__(self, sys_path, time_delta_hour, base_name)
        # виды клавиатур
        self.KBRD_HEADMAN = "headman"
        self.KBRD_MAKE_ANN = "make_announcement"
        # главное меню -------------------------------------------------------------------------------------------------
        buttons = [[self.keyboards.get_button(label="Расписание пар", color="default", payload="Couples_sch"),
                    self.keyboards.get_button(label="Расписание звонков", color="default", payload="Call_sch")],
                   [self.keyboards.get_button(label="Тип недели", color="default", payload="Type_of_week")],
                   [self.keyboards.get_button(label="Учебный план", color="default", payload="Academic_plan")],
                   [self.keyboards.get_button(label="Настройки", color="default", payload="Settings"),
                    self.keyboards.get_button(label="Режим бога", color="negative", payload="Headman_Settings")]]
        self.keyboards.addKeyboard(self.KBRD_MENU, False, None, buttons)
        # главное меню старосты ----------------------------------------------------------------------------------------
        buttons = [[self.keyboards.get_button(label="Сделать объявление", color="positive", payload="Make_announcement")],
                   [self.keyboards.get_button(label="Главное меню", color="negative", payload="Main_menu")]]
        self.keyboards.addKeyboard(self.KBRD_HEADMAN, False, None, buttons)
        # пустая клавиатура --------------------------------------------------------------------------------------------
        buttons = [[self.keyboards.get_button(label="Главное меню", color="negative", payload="Main_menu")]]
        self.keyboards.addKeyboard(self.KBRD_MAKE_ANN, False, None, buttons)

    def _menus_processing(self, user_meta: user.User, message: dict = ()):
        # получаем последнюю команду (в файл записываются только те, что имеют контекст, например открытое меню)
        end_command = self.database.get_user_end_command(user_meta.user_id)
        # проверяем последние действия пользователя с  контекстом
        if end_command == self.KBRD_HEADMAN:  # если последнее действие - открытие меню старосты
            return self._menu_headman(user_meta, message)
        if end_command == self.KBRD_MAKE_ANN:
            return self._make_announcement(user_meta, message)
        else:  # если последнее действие - не является командой старосты то вызываем родителя
            return Command._menus_processing(self, user_meta, message)

    def _menu_main(self, user_meta: user.User, message: dict = ()):
        response = Command._menu_main(self, user_meta, message)
        if response is not None:
            return response
        else: # если не найдены команды из обычного меню то проверяем команды старосты
            try:
                payload = json.loads(message["payload"])["button"]
                if "Headman_Settings" == payload:
                    self.database.write_user_end_command(user_meta.user_id, self.KBRD_HEADMAN)
                    return {self.ANS_MESSAGE: "{0}, у тебя есть права старосты!".format(user_meta.first_name),
                            self.ANS_KEYBOARD: self.keyboards.getKeyboard(self.KBRD_HEADMAN),
                            self.ANS_PEER_ID: user_meta.user_id,
                            self.AMS_RAND_ID: random.randint(1, 2147483647)}
            except Exception as e:
                return

    def _menu_headman(self, user_meta: user.User, message: dict = ()):
        try:
            payload = json.loads(message["payload"])["button"]
            if "Main_menu" == payload:
                self.database.write_user_end_command(user_meta.user_id, "")
                return {self.ANS_MESSAGE: "{0}, выбери один из вариантов:".format(user_meta.first_name),
                        self.ANS_KEYBOARD: self.keyboards.getKeyboard(self.KBRD_MENU),
                        self.ANS_PEER_ID: user_meta.user_id,
                        self.AMS_RAND_ID: random.randint(1, 2147483647)}
            if "Make_announcement" == payload:
                self.database.write_user_end_command(user_meta.user_id, self.KBRD_MAKE_ANN)
                return {self.ANS_MESSAGE: "{0}, Введите текст объяявления:".format(user_meta.first_name),
                        self.ANS_KEYBOARD: self.keyboards.getKeyboard(self.KBRD_MAKE_ANN),
                        self.ANS_PEER_ID: user_meta.user_id,
                        self.AMS_RAND_ID: random.randint(1, 2147483647)}
        except Exception as e:
            return

    def _make_announcement(self, user_meta: user.User, message: dict = ()):
        if "payload" in message:
            payload = json.loads(message["payload"])
            if "button" in payload:
                payload = payload["button"]
                if "Main_menu" == payload:
                    self.database.write_user_end_command(user_meta.user_id, "")
                    return {self.ANS_MESSAGE: "{0}, выбери один из вариантов:".format(user_meta.first_name),
                            self.ANS_KEYBOARD: self.keyboards.getKeyboard(self.KBRD_MENU),
                            self.ANS_PEER_ID: user_meta.user_id,
                            self.AMS_RAND_ID: random.randint(1, 2147483647)}
        self.database.write_user_end_command(user_meta.user_id, self.KBRD_HEADMAN)
        # получаем id людей нашей группы
        group_id = self.database.get_group_id(user_id=user_meta.user_id)
        users_ids = self.database.get_group_users_ids(group_id)
        answers = []
        for user_id in users_ids:
            answers.append({self.ANS_MESSAGE: message["text"],
                            self.ANS_PEER_ID: user_id,
                            self.AMS_RAND_ID: random.randint(1, 2147483647)})
            # в ответ, который пойдет старосте пишем другие данные
            if user_id == user_meta.user_id:
                answers[-1][self.ANS_MESSAGE] = "Объявление успешно отправлено"
                answers[-1][self.ANS_KEYBOARD] = self.KBRD_HEADMAN
        return answers