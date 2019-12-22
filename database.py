import json
import os

from peewee import *


class DataBase():
    def __init__(self, sys_path: str = ".", file_name: str = "default"):
        self.file_name = file_name + ".db"
        self.sys_path = sys_path
        self.folder_path = sys_path + "\\data_base"
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)
        self.db = SqliteDatabase("{0}\\{1}".format(self.folder_path, self.file_name))

        class BaseModel(Model):
            class Meta:
                database = self.db

        class Faculties(BaseModel):
            Name = CharField()

        class Departments(BaseModel):
            Name = CharField()
            Faculty = ForeignKeyField(Faculties, related_name='Department_faculty')

        class Groups(BaseModel):
            Name = CharField()
            Timetable = BlobField()
            Department = ForeignKeyField(Departments, related_name='Group_department')

        class Users(BaseModel):
            User_id = BigIntegerField()
            End_command = CharField(null=True)
            Buffer_str = CharField(null=True)
            Morning_mailing = BooleanField()
            Evening_mailing = BooleanField()
            Headman = BooleanField()
            Group = ForeignKeyField(Groups, related_name='Group_user')

        self.Faculties = Faculties
        self.Departments = Departments
        self.Groups = Groups
        self.Users = Users

        if not os.path.isfile("{0}\\{1}".format(self.folder_path, self.file_name)):
            self.db.connect()
            self.Faculties.create_table()
            self.Departments.create_table()
            self.Groups.create_table()
            self.Users.create_table()
        else:
            self.db.connect()

    """
    временно
    заменить наотправку запроса о том что человека нет и пусть он введет свою группу
    """

    def init_user(self, user_id=None, group_id=None, buffer: str = "",
                  end_command: str = "", headman: bool = False,
                  morning: bool = True, evening: bool = True):
        if type(user_id) == int and type(group_id) == int:
            user = self.Users.select().where(self.Users.User_id == user_id)
            group_row = self.Groups.select().where(self.Groups.id == group_id)
            if group_row.exists():
                if user.exists():
                    user.first().Group = group_row.first()
                    user.first().End_command = end_command
                    user.first().headman = headman
                    user.first().Morning_mailing = morning
                    user.first().Evening_mailing = evening
                    user.first().Buffer_str = buffer
                    user.first().save()
                else:
                    self.Users.create(User_id=user_id,
                                      End_command=end_command,
                                      Buffer_str=buffer,
                                      Morning_mailing=morning,
                                      Evening_mailing=evening,
                                      Headman=headman,
                                      Group=group_row.first())
                return True
        return False

    def load_user(self, user_id=None):
        if type(user_id) == int:
            user = self.Users.select().where(self.Users.User_id == user_id)
            if user.exists():
                return True
        return False


    def get_morning_m(self, user_id=None):
        if user_id is not None:
            users = self.Users.select().where(self.Users.User_id == int(user_id))
            if users.exists():
                return bool(users.first().Morning_mailing)
        return False

    def get_evening_m(self, user_id=None):
        if user_id is not None:
            users = self.Users.select().where(self.Users.User_id == int(user_id))
            if users.exists():
                return bool(users.first().Evening_mailing)
        return False

    def get_group_name(self, user_id=None):
        if type(user_id) == int:
            users = self.Users.select().where(self.Users.User_id == group_id)
            if users.exists():
                return users.first().Group.Name
        return

    def get_group_id(self, user_id=None, group_name=None):
        if type(group_name) == str:
            groups = self.Groups.select().where(self.Groups.Name == group_name)
            if groups.exists():
                return groups.first().id
        if type(user_id) == int:
            users = self.Users.select().where(self.Users.User_id == user_id)
            if users.exists():
                return users.first().Group_id
        elif type(user_id) == int and type(group_name) == str:
            users = self.Users.select().where(self.Users.User_id == user_id, self.Users.Group.name == group_name)
            if users.exists():
                return users.first().Group_id
        return

    def get_groups_names(self):
        groups = self.Groups.select()
        if groups.exists():
            return [a.Name for a in groups]
        return []

    def get_department_name(self, user_id=None):
        if user_id is not None:
            users = self.Users.select().where(self.Users.User_id == int(user_id))
            if users.exists():
                return users.first().Group.Department.Name
        return

    def get_group_users_ids(self, group_id=None):
        if group_id is not None:
            users = self.Users.select().where(self.Users.Group == group_id)
            if users.exists():
                return [a.User_id for a in users]
        return []

    def get_department_ids(self, department_name=None):
        if department_name is None:
            return
        users = self.Users.select().join(self.Groups).join(self.Departments).where(
            self.Departments.Name == str(department_name))
        if users.exists():
            return [a.User_id for a in users]
        return

    def get_all_ids_groups(self):
        groups = self.Groups.select(self.Groups.id)
        if groups.exists():
            return [group.id for group in groups]
        return []

    def get_timetable(self, group_id=None):
        if group_id is not None:
            timetable = self.Groups.select(self.Groups.Timetable).where(self.Groups.id == int(group_id))
            if timetable.exists():
                return json.loads(timetable.first().Timetable)
        return

    def get_user_end_command(self, user_id=None):
        if type(user_id) == int:
            end_command = self.Users.select().where(self.Users.User_id == user_id)
            if end_command.exists():
                return end_command.first().End_command

    def write_user_end_command(self, user_id=None, end_command: str = ""):
        if type(user_id) == int:
            user = self.Users.select().where(self.Users.User_id == user_id)
            if user.exists():
                user.first().End_command = end_command
                user.first().save()

    def get_user_morning_m(self, user_id=None):
        if type(user_id) == int:
            result = self.Users.select().where(self.Users.User_id == user_id)
            if result.exists():
                return bool(result.first().Morning_mailing)
        return False

    def write_user_morning_m(self, user_id=None, value: int = 1):
        if type(user_id) == int:
            user = self.Users.select().where(self.Users.User_id == user_id)
            if user.exists():
                user.first().Morning_mailing = value
                user.first().save()

    def get_user_evening_m(self, user_id=None):
        if type(user_id) == int:
            result = self.Users.select().where(self.Users.User_id == user_id)
            if result.exists():
                return bool(result.first().Evening_mailing)
        return False

    def write_user_evening_m(self, user_id=None, value: int = 1):
        if type(user_id) == int:
            user = self.Users.select().where(self.Users.User_id == user_id)
            if user.exists():
                user.first().Evening_mailing = value
                user.first().save()

    def get_user_headman(self, user_id=None):
        if type(user_id) == int:
            result = self.Users.select().where(self.Users.User_id == user_id)
            if result.exists():
                return bool(result.first().Headman)
            return False

    def delete_user(self, user_id=None):
        if type(user_id) == int:
            users = self.Users.select().where(self.Users.User_id == user_id)
            if users.exists():
                users.first().delete_instance()

    def _TEST_create(self):
        timetab = {
            "top": {
                "1": {
                    "2": {
                        "discipline": "Технологии компьютерного проектирования",
                        "class": "11.401",
                        "teacher": "Гудаев О.А",
                        "type": "лекция"
                    },
                    "3": {
                        "discipline": "Программное обеспечение сетей",
                        "class": "11.412",
                        "teacher": "Сорокин Р.А.",
                        "type": "лекция"
                    }
                },
                "2": {
                    "1": {
                        "discipline": "Технологии распределительных систем и параллельных вычислений",
                        "class": "11.402",
                        "teacher": "Едемская Е.Н.",
                        "type": "лекция"
                    },
                    "2": {
                        "discipline": "Стандартизация и сертификация в сфере IT",
                        "class": "6.309",
                        "teacher": "Клименко И.В.",
                        "type": "лекция"
                    },
                    "3": {
                        "discipline": "Стандартизация и сертификация в сфере IT",
                        "class": "6.306",
                        "teacher": "Клименко И.В.",
                        "type": "лабораторная"
                    }
                },
                "3": {
                    "2": {
                        "discipline": "Технологии распределительных систем и параллельных вычислений",
                        "class": "11.401",
                        "teacher": "Едемская Е.Н.",
                        "type": "лабораторная"
                    },
                    "3": {
                        "discipline": "Web-технологияя и web-программирование",
                        "class": "11.403",
                        "teacher": "Сорокин Р.А.",
                        "type": "лекция"
                    },
                    "4": {
                        "discipline": "Менеджмент",
                        "class": "3 корпус т.ц. №1",
                        "teacher": "Попова Е.А.",
                        "type": "лекция"
                    }
                },
                "4": {
                    "3": {
                        "discipline": "Технологии создания программных продуктов",
                        "class": "11.403",
                        "teacher": "Маслова Е.А.",
                        "type": "лекция"
                    },
                    "4": {
                        "discipline": "Корпоративные информационные системы",
                        "class": "11.412",
                        "teacher": "Ольшевский А.И.",
                        "type": "лабораторная"
                    }
                },
                "5": {
                    "2": {
                        "discipline": "Корпоративные информационные системы",
                        "class": "11.402",
                        "teacher": "Ольшевский А.И.",
                        "type": "лекция"
                    },
                    "3": {
                        "discipline": "Менеджмент",
                        "class": "3.309а",
                        "teacher": "Попова Е.А.",
                        "type": "практика"
                    }
                }
            },
            "lower": {
                "1": {
                    "2": {
                        "discipline": "Технологии компьютерного проектирования",
                        "class": "11.411",
                        "teacher": "Гудаев О.А",
                        "type": "лабораторная"
                    },
                    "3": {
                        "discipline": "Программное обеспечение сетей",
                        "class": "11.412",
                        "teacher": "Сорокин Р.А.",
                        "type": "лекция"
                    },
                    "4": {
                        "discipline": "Web-технологияя и web-программирование",
                        "class": "11.411",
                        "teacher": "Радевич Е.В.",
                        "type": "лабораторная"
                    }
                },
                "2": {
                    "1": {
                        "discipline": "Технологии распределительных систем и параллельных вычислений",
                        "class": "11.402",
                        "teacher": "Едемская Е.Н.",
                        "type": "лекция"
                    },
                    "2": {
                        "discipline": "Стандартизация и сертификация в сфере IT",
                        "class": "6.309",
                        "teacher": "Клименко И.В.",
                        "type": "лекция"
                    }
                },
                "3": {
                    "1": {
                        "discipline": "Технологии создания программных продуктов",
                        "class": "11.403",
                        "teacher": "Маслова Е.А.",
                        "type": "лабораторная"
                    },
                    "2": {
                        "discipline": "Технологии распределительных систем и параллельных вычислений",
                        "class": "11.401",
                        "teacher": "Едемская Е.Н.",
                        "type": "лабораторная"
                    },
                    "3": {
                        "discipline": "Web-технологияя и web-программирование",
                        "class": "11.403",
                        "teacher": "Сорокин Р.А.",
                        "type": "лекция"
                    },
                    "4": {
                        "discipline": "Менеджмент",
                        "class": "3 корпус т.ц. №1",
                        "teacher": "Попова Е.А.",
                        "type": "лекция"
                    }
                },
                "4": {
                    "3": {
                        "discipline": "Технологии создания программных продуктов",
                        "class": "11.403",
                        "teacher": "Маслова Е.А.",
                        "type": "лекция"
                    },
                    "4": {
                        "discipline": "Корпоративные информационные системы",
                        "class": "11.412",
                        "teacher": "Ольшевский А.И.",
                        "type": "лабораторная"
                    }
                },
                "5": {
                    "2": {
                        "discipline": "Корпоративные информационные системы",
                        "class": "11.402",
                        "teacher": "Ольшевский А.И.",
                        "type": "лекция"
                    },
                    "3": {
                        "discipline": "Программное обеспечение сетей",
                        "class": "11.411",
                        "teacher": "Сорокин Р.А.",
                        "type": "лабораторная"
                    }
                }
            }
        }
        timetab = json.dumps(timetab).encode("utf-8")

        self.Faculties.create(Name="КНТ")
        self.Faculties.create(Name="КИТА")
        self.Faculties.create(Name="ИЭФ")

        self.Departments.create(Name="ИИСА", Faculty=1)
        self.Departments.create(Name="КС", Faculty=2)
        self.Departments.create(Name="ПИ", Faculty=1)
        self.Departments.create(Name="ЭКО", Faculty=3)

        self.Groups.create(Name="СИИ-16", Timetable=timetab,
                           Department=self.Departments.get(self.Departments.Name == "ИИСА"))
        self.Groups.create(Name="ПОВТ-16", Timetable=timetab,
                           Department=self.Departments.get(self.Departments.Name == "ИИСА"))
        self.Groups.create(Name="ПИ-16", Timetable=timetab,
                           Department=self.Departments.get(self.Departments.Name == "ПИ"))
        """
        self.Groups.create(Name="СИИ-16", Timetable=str.encode("Тут что то есть 😋", encoding='utf-8'),
                           Department=self.Departments.get(self.Departments.Name == "ИИСА"))
        """
        self.init_user(88233396, "СИИ-16", headman=True)
        self.init_user(216634551, "СИИ-16")
        self.init_user(151232514, "СИИ-16")


if __name__ == "__main__":
    dataPath = os.path.expanduser('~') + "\\.VK Bot 2\\test"
    if not os.path.exists(dataPath):
        os.makedirs(dataPath)


    data = DataBase(dataPath,"DonNTU")
    data._TEST_create()

    print(data.get_all_ids_groups())
    print(data.get_timetable(1))
    """
    print(data.init_user(21000, "СИИ-16"))
    print(data.init_user(22000, "СИИ-16"))
    print(data.init_user(23000, "СИИ-16"))
    print(data.init_user(24000, "СИИ-16"))
    print(data.init_user(10000, "ПИ-16"))
    print(data.init_user(10000))
    print(data.init_user(10001))

    print(data.get_group_name(10000))
    """
    print(data.get_department_name(10000))
    print(data.get_department_ids("ИИСА"))
"""
    iisa = Departments.select().where(Departments.Name == "ПИ")
    if iisa.exists():
        print(iisa[0])

    for dp in Departments.select():
        print(dp.Name, dp.Faculty.Name)

    for fc in Faculties.select():
        print(fc.Name, "Departments:", fc.Department_faculty.count())
        for dp in fc.Department_faculty:
            print("     " + dp.Name)
"""
