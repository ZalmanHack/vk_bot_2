import os

from peewee import *

db = None


class DataBase():
    def __init__(self, sys_path: str = ".", file_name: str = "default"):
        self.file_name = file_name + ".db"
        self.folder_path = sys_path + "\\data_base"
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)
        global db
        db = SqliteDatabase(self.folder_path + "\\" + self.file_name)
        if not os.path.isfile(self.folder_path + "\\" + self.file_name):
            Faculties.create_table()
            Departments.create_table()
            Groups.create_table()
            Commands.create_table()
            Users.create_table()

    def init_user(self, user_id=None, group=None):
        if user_id is None:
            return False
        else:
            user = Users.select().where(Users.User_id == int(user_id))
            if user.exists():
                if group is not None:
                    group_row = Groups.select().where(Groups.Name == str(group))
                    if user.first().Group.Name != str(group) and group_row.exists():
                        user.first().Group = group_row.first()
                        user.first().save()
            else:
                group_rows = Groups.select().where(Groups.Name == str(group))
                if group_rows.exists():
                    Users.create(User_id=user_id, End_command=1, Morning_mailing=1, Evening_mailing=1, Headman=0,
                                 Group=group_rows[0])
                else:
                    return False
        return True

    def get_group_name(self, user_id=None):
        if user_id is None:
            return False
        users = Users.select().where(Users.User_id == int(user_id))
        if users.exists():
            return users.first().Group.Name
        else:
            return False

    def get_department_name(self, user_id=None):
        if user_id is None:
            return False
        users = Users.select().where(Users.User_id == int(user_id))
        if users.exists():
            return users.first().Group.Department.Name
        else:
            return False

    def get_group_ids(self, group_name=None):
        if group_name is None:
            return False
        users = Users.select().join(Groups).where(Groups.Name == str(group_name))
        if users.exists():
            return [a.User_id for a in users]
        return False

    def get_department_ids(self, department_name=None):
        if department_name is None:
            return False
        users = Users.select().join(Groups).join(Departments).where(Departments.Name == str(department_name))
        if users.exists():
            return [a.User_id for a in users]
        return False



db = SqliteDatabase("my_app.db")


class Faculties(Model):
    Name = CharField()

    class Meta:
        database = db  # модель будет использовать базу данных 'people.db'


class Departments(Model):
    Name = CharField()
    Faculty = ForeignKeyField(Faculties, related_name='Department_faculty')

    class Meta:
        database = db  # модель будет использовать базу данных 'people.db'


class Groups(Model):
    Name = CharField()
    Department = ForeignKeyField(Departments, related_name='Group_department')

    class Meta:
        database = db  # модель будет использовать базу данных 'people.db'


class Commands(Model):
    Name = CharField()

    class Meta:
        database = db  # модель будет использовать базу данных 'people.db'


class Users(Model):
    User_id = CharField()
    End_command = ForeignKeyField(Commands, related_name='User_end_command')
    Morning_mailing = BooleanField()
    Evening_mailing = BooleanField()
    Headman = BooleanField()
    Group = ForeignKeyField(Groups, related_name='Group_user')

    class Meta:
        database = db  # модель будет использовать базу данных 'people.db'


def create():

    Commands.create_table()
    Commands.create(Name="Операция")

    Faculties.create_table()
    Faculties.create(Name="КНТ")
    Faculties.create(Name="КИТА")
    Faculties.create(Name="ИЭФ")

    Departments.create_table()
    Departments.create(Name="ИИСА", Faculty=1)
    Departments.create(Name="КС", Faculty=2)
    Departments.create(Name="ПИ", Faculty=1)
    Departments.create(Name="ЭКО", Faculty=3)

    Groups.create_table()
    Groups.create(Name="СИИ-16", Department=Departments.get(Departments.Name == "ИИСА"))
    Groups.create(Name="ПОИС-16", Department=Departments.get(Departments.Name == "ИИСА"))
    Groups.create(Name="ПИ-16", Department=Departments.get(Departments.Name == "ПИ"))

if __name__ == "__main__":
    # db = DataBase(file_name="test")
    # db.get_group_by_id(20000)

    data = DataBase(file_name="my_app.db")
    print(data.init_user(21000, "СИИ-16"))
    print(data.init_user(22000, "СИИ-16"))
    print(data.init_user(23000, "СИИ-16"))
    print(data.init_user(24000, "СИИ-16"))
    print(data.init_user(10000, "ПИ-16"))


    print(data.get_group_name(10000))
    print(data.get_group_ids("СИИ-16"))

    print(data.get_department_name(10000))
    print(data.get_department_ids("ИИСА"))

    print(Users.select().where(Users.Group.Name == "ПИ-16"))
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


