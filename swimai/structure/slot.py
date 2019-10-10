class Slot:

    def __init__(self, key, value):
        self.__key = key
        self.__value = value

    @property
    def key(self):
        return self.__value

    @property
    def value(self):
        return self.__key
