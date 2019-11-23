class KeyBoard():
    def __init__(self):
        self._keyboard = {}
    def get_button(self, label, color, payload):
        return {"action": {"type": "text", "label": label, "payload": "{\"button\": \"" + str(payload) + "\"}"},
                "color": color}

    def addKeyboard(self, name: str = "default", one_time: bool = None, inline: bool = None, buttons: list = ()):
        self._keyboard[name] = {}
        if inline is not None:
            self._keyboard[name]["inline"] = inline
        elif one_time is not None:
            self._keyboard[name]["one_time"] = one_time
        self._keyboard[name]["buttons"] = buttons
        return self._keyboard[name]

    def getKeyboard(self, name: str = "default"):
        return self._keyboard[name]


if __name__ == "__main__":
    test = KeyBoard()
    test.get_button("1", "2", "3")
    test.get_button("4", "5", "6")
    test.addKeyboard("test", False, True, [test.get_button("1", "2", "3"), test.get_button("4", "5", "6")])
