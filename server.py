import datetime
import json
import os
import random
import sys
import time
from threading import Thread

import requests
import vk_api
from vk_api.bot_longpoll import VkBotEventType
from vk_api.bot_longpoll import VkBotLongPoll

import command_headman
import database
import logining


class Server:

    def __init__(self, api_token, group_id, sys_path: str = "", server_name: str = "Empty", time_delta_hour: int = 3):
        # инициализируем часовой пояс
        self.time_delta_hour = time_delta_hour
        self.time_delta = datetime.timedelta(hours=self.time_delta_hour, minutes=0)
        # Даем серверу имя
        self.server_name = server_name
        # запоминаем id группы
        self.group_id = group_id
        # создаем папку сервера
        self.folder_path = sys_path + "\\" + server_name
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)
        # --------------------------------------------------------------------------------------------------------------
        # Для Long Poll
        self.vk = vk_api.VkApi(token=api_token)
        # Для использования Long Poll API
        self.long_poll = VkBotLongPoll(self.vk, group_id)
        # Для вызова методов vk_api
        self.vk_api = self.vk.get_api()
        # --------------------------------------------------------------------------------------------------------------
        # инициализация класса, обрабатывающего команды
        self.command = command_headman.Command_headman(self.folder_path, self.time_delta_hour)
        self.log = logining.Logining(self.folder_path, self.time_delta_hour)
        # --------------------------------------------------------------------------------------------------------------
        # инициализация базы данных
        self.database = database.DataBase(sys_path, "data-test-bot")

    def _get_document(self, file_path, file_name, owner_id):
        try:
            # получение ссылки куда будет загружен файл
            upload_url = self.vk.method("docs.getMessagesUploadServer", {"type": "doc", "peer_id": owner_id})[
                "upload_url"]
            # print(upload_url)
            # отправляем файл на загрузку
            response = requests.post(upload_url, files={"file": open(file_path, "rb")})
            # получаем json файл  данными о нем
            result = json.loads(response.text)
            file = result["file"]
            # сохраняем файл
            f_json = self.vk.method("docs.save", {"file": file, "title": file_name})
            # print(json.dumps(f_json, indent=4))
            # ля корректного отображения документа в сообщении
            attach = 'doc' + str(owner_id) + '_' + str(f_json["doc"]["id"])
            # отправка сообщения
            # json "attachment"
            return attach
        except Exception as e:
            self.log.error(sys._getframe().f_code.co_name, e.args)
            return ""

    def _get_user_name(self, user_id):
        user = self.vk_api.users.get(user_id=user_id)[0]
        return [user["first_name"], user["last_name"]]

    def _upload_attachment(self, answer: dict = ()):
        if "attachment" in answer:
            file_path = answer["attachment"]["file_path"]
            file_name = answer["attachment"]["file_name"]
            peer_id = answer["peer_id"]
            result = self._get_document(file_path, file_name, peer_id)
            if len(result) == 0:
                answer.pop("attachment")
                answer["message"] = "Файл не найден"
                return answer
            answer["attachment"] = result
        return answer

    def _decode_keyboard(self, answer: dict = ()):
        try:
            answer["keyboard"] = json.dumps(answer["keyboard"], ensure_ascii=False).encode("utf-8").decode("utf-8")
            return answer
        except Exception as e:
            return answer  # logining(sys._getframe().f_code.co_name, E.args)

    def _send_message(self, message=None, peer_id=None, text=None, keyboard=None, attachment=None):
        try:
            if message is None:
                message: dict = {"peer_id": peer_id, "message": text, "random_id": random.randint(1, 2147483647)}
                if keyboard is not None:
                    message["keyboard"] = keyboard
                if attachment is not None:
                    message["attachment"] = attachment
            self.vk.method("messages.send", message)
        except Exception as e:
            # logining(sys._getframe().f_code.co_name, E.args)
            return False
        return True

    def mailing(self):
        while True:
            print("mailing")
            answer = None
            # получаекм список участников сообщества
            all_groups_id = self.vk.method("groups.getMembers", {"group_id": str(self.group_id)})["items"]
            _time = datetime.datetime.now(datetime.timezone.utc) + self.time_delta
            for id in all_groups_id:
                first_name, last_name = self._get_user_name(id)
                answer = self.command.mailing(id, first_name, last_name, "timetable", _time)
                if answer is None:
                    break
                elif answer is not False:
                    self._send_message(answer)
            if answer is not None:
                time.sleep(100)  # если ответ не пустота то пары есть, нужно заснуть чтобы не было повторной расслыки
            self.log.error(sys._getframe().f_code.co_name, "123")

    def is_follower(self, id=None):
        if id is not None:
            all_groups_id = self.vk.method("groups.getMembers", {"group_id": str(self.group_id)})["items"]
            if int(id) in all_groups_id:
                return True
        return False

    # API ПОДОБРАТЬ !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    def listen(self):
        for event in self.long_poll.listen():  # Слушаем сервер
            # Пришло новое сообщение
            if event.type == VkBotEventType.MESSAGE_NEW:
                user_id = event.object["message"]["from_id"]
                first_name, second_name = self._get_user_name(user_id)
                if self.is_follower(user_id):
                    message = event.object["message"]
                    answer = self.command.message(user_id, first_name, second_name, message)
                    answer = self._upload_attachment(answer)
                    answer = self._decode_keyboard(answer)
                    self._send_message(answer)
                else:
                    self._send_message(peer_id=user_id, text=first_name + ", сначала подпишитесь на сообщество!")


if __name__ == "__main__":
    dataPath = os.path.expanduser('~') + "\\.VK Bot 2"
    if not os.path.exists(dataPath):
        os.makedirs(dataPath)
    token = "c3eb50d9421632ce5bfb3927d54f27118e2d90307792e70f9212b5ba075403d076c29a342d8ab157c2368"
    group_id = 80694145
    server = "test"
    serv = Server(token, group_id, dataPath, server, 2)
    p2 = Thread(target=serv.mailing)
    p1 = Thread(target=serv.listen)
    p1.start()
    # p2.start()
