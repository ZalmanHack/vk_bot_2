import command

class Command_headman(command.Command):
    def __init__(self, sys_path: str = "", time_delta_hour: int = 3):
        command.Command.__init__(self, sys_path, time_delta_hour)
        # главное меню -------------------------------------------------------------------------------------------------
        buttons = [[self.keyboards.get_button(label="Расписание пар", color="default", payload="Couples_sch"),
                    self.keyboards.get_button(label="Расписание звонков", color="default", payload="Call_sch")],
                   [self.keyboards.get_button(label="Тип недели", color="default", payload="Type_of_week")],
                   [self.keyboards.get_button(label="Учебный план", color="default", payload="Academic_plan")],
                   [self.keyboards.get_button(label="Настройки рассылки", color="default", payload="Mailing_Settings"),
                    self.keyboards.get_button(label="Режим бога", color="negative", payload="Headman_Settings")]]
        self.keyboards.addKeyboard(self.KBRD_MENU, False, None, buttons)

