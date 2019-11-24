import os

from peewee import *


class DataBase():
    def __init__(self, sys_path: str = ".", file_name: str = "default"):
        self.file_name = file_name + ".db"
        self.sys_path = sys_path
        self.folder_path = sys_path + "/data_base"
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)
        self.db = SqliteDatabase("{0}/{1}".format(self.folder_path, self.file_name))

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
            Department = ForeignKeyField(Departments, related_name='Group_department')

        class Commands(BaseModel):
            Name = CharField()

        class Users(BaseModel):
            User_id = CharField()
            End_command = ForeignKeyField(Commands, related_name='User_end_command')
            Buffer_data = BlobField(null=True)
            Morning_mailing = BooleanField()
            Evening_mailing = BooleanField()
            Headman = BooleanField()
            Group = ForeignKeyField(Groups, related_name='Group_user')

        self.Faculties = Faculties
        self.Departments = Departments
        self.Groups = Groups
        self.Commands = Commands
        self.Users = Users

        if not os.path.isfile("{0}/{1}".format(self.folder_path, self.file_name)):
            self.db.connect()
            self.Faculties.create_table()
            self.Departments.create_table()
            self.Groups.create_table()
            self.Commands.create_table()
            self.Users.create_table()
        else:
            self.db.connect()

    """
    временно
    заменить наотправку запроса о том что человека нет и пусть он введет свою группу
    """

    def init_user(self, user_id=None, group=None):
        if user_id is None:
            return False
        else:
            user = self.Users.select().where(self.Users.User_id == int(user_id))
            if user.exists():
                if group is not None:
                    group_row = self.Groups.select().where(self.Groups.Name == str(group))
                    if user.first().Group.Name != str(group) and group_row.exists():
                        user.first().Group = group_row.first()
                        user.first().save()
            else:
                group_rows = self.Groups.select().where(self.Groups.Name == str(group))
                if group_rows.exists():
                    self.Users.create(User_id=user_id, End_command=1, Buffer_data="2222", Morning_mailing=1,
                                      Evening_mailing=1, Headman=0,
                                      Group=group_rows.first())
                else:
                    return False
        return True

    def get_group_name(self, user_id=None):
        if user_id is None:
            return False
        users = self.Users.select().where(self.Users.User_id == int(user_id))
        if users.exists():
            return users.first().Group.Name
        else:
            return False

    def get_department_name(self, user_id=None):
        if user_id is None:
            return False
        users = self.Users.select().where(self.Users.User_id == int(user_id))
        if users.exists():
            return users.first().Group.Department.Name
        else:
            return False

    def get_group_ids(self, group_name=None):
        if group_name is None:
            return False
        users = self.Users.select().join(self.Groups).where(self.Groups.Name == str(group_name))
        if users.exists():
            return [a.User_id for a in users]
        return False

    def get_department_ids(self, department_name=None):
        if department_name is None:
            return False
        users = self.Users.select().join(self.Groups).join(self.Departments).where(
            self.Departments.Name == str(department_name))
        if users.exists():
            return [a.User_id for a in users]
        return False

    def _TEST_create(self):
        self.Commands.create(Name="Операция")

        self.Faculties.create(Name="КНТ")
        self.Faculties.create(Name="КИТА")
        self.Faculties.create(Name="ИЭФ")

        self.Departments.create(Name="ИИСА", Faculty=1)
        self.Departments.create(Name="КС", Faculty=2)
        self.Departments.create(Name="ПИ", Faculty=1)
        self.Departments.create(Name="ЭКО", Faculty=3)

        self.Groups.create(Name="СИИ-16", Department=self.Departments.get(self.Departments.Name == "ИИСА"))
        self.Groups.create(Name="ПОИС-16", Department=self.Departments.get(self.Departments.Name == "ИИСА"))
        self.Groups.create(Name="ПИ-16", Department=self.Departments.get(self.Departments.Name == "ПИ"))


class Faculties(Model):
    Name = CharField()


class Departments(Model):
    Name = CharField()
    Faculty = ForeignKeyField(Faculties, related_name='Department_faculty')


class Groups(Model):
    Name = CharField()
    Department = ForeignKeyField(Departments, related_name='Group_department')


class Commands(Model):
    Name = CharField()


class Users(Model):
    User_id = CharField()
    End_command = ForeignKeyField(Commands, related_name='User_end_command')
    Morning_mailing = BooleanField()
    Evening_mailing = BooleanField()
    Headman = BooleanField()
    Group = ForeignKeyField(Groups, related_name='Group_user')


if __name__ == "__main__":
    data = DataBase(file_name="DonNTU")
    data._TEST_create()

    print(data.init_user(21000, "СИИ-16"))
    print(data.init_user(22000, "СИИ-16"))
    print(data.init_user(23000, "СИИ-16"))
    print(data.init_user(24000, "СИИ-16"))
    print(data.init_user(10000, "ПИ-16"))
    print(data.init_user(10000))
    print(data.init_user(10001))

    print(data.get_group_name(10000))
    print(data.get_group_ids("СИИ-16"))

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
