from swimai.structure.field import Field
from swimai.structure.value import Text


class Attr(Field):

    def __init__(self, key, value):
        self.__key = key
        self.__value = value

    @property
    def key(self):
        return self.__key

    @property
    def value(self):
        return self.__value

    @staticmethod
    def of(key, value):

        if key is None:
            raise TypeError('key')

        if value is None:
            raise TypeError('value')

        return Attr(Text.get_from(key), value)
