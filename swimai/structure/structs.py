from abc import ABC, abstractmethod
from enum import Enum


class Item(ABC):

    @property
    @abstractmethod
    def key(self):
        ...

    @staticmethod
    def extant():
        return Extant.get_extant()

    def concat(self, new_item):

        record = Record.create()
        record.add(self)

        if isinstance(new_item, Record):
            record.add_all(new_item)
        else:
            record.add(new_item)

        return record


class Field(Item, ABC):

    @property
    @abstractmethod
    def key(self):
        ...

    @property
    @abstractmethod
    def value(self):
        ...


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


class Value(Item):

    @property
    def key(self):
        return Value.absent()

    @staticmethod
    def absent():
        return Absent.get_absent()

    def to_value(self):
        return self

    def length(self):
        return 0


class Text(Value):
    empty = None

    def __init__(self, value):
        self.value = value

    @staticmethod
    def get_from(string):
        if not string:
            return Text.get_empty()
        return Text(string)

    @staticmethod
    def get_empty():
        if Text.empty is None:
            Text.empty = Text('')

        return Text.empty

    def string_value(self):
        return self.value


class Bool(Value):
    TRUE = None
    FALSE = None

    def __init__(self, value):
        self.value = value

    @staticmethod
    def get_from(value):

        if value:
            if Bool.TRUE is None:
                Bool.TRUE = Bool(True)

            return Bool.TRUE
        else:
            if Bool.FALSE is None:
                Bool.FALSE = Bool(False)

            return Bool.FALSE


class Absent(Value):
    absent = None

    @staticmethod
    def get_absent():
        if Absent.absent is None:
            Absent.absent = Absent()

        return Absent.absent


class Slot(Field):

    def __init__(self, key, value):
        self.__key = key
        self.__value = value

    @property
    def key(self):
        return self.__key

    @property
    def value(self):
        return self.__value


class Extant(Value):
    extant = None

    @staticmethod
    def get_extant():
        if Extant.extant is None:
            Extant.extant = Extant()

        return Extant()


class Record(Value, ABC):

    @staticmethod
    def create():
        return RecordMap.create()

    @abstractmethod
    def add(self, item):
        ...

    def add_all(self, items):
        changed = False

        for item in items:
            self.add(item)
            changed = True

        return changed

    def slot(self, key, value):

        if isinstance(key, str):
            key = Text.get_from(key)

        if isinstance(value, str):
            value = Text.get_from(value)

        self.add(Slot(key, value))
        return self

    @property
    @abstractmethod
    def size(self):
        ...

    def length(self):
        return self.size


class RecordFlags(Enum):
    IMMUTABLE = 1 << 0
    ALIASED = 1 << 1


class RecordMap(Record):

    def __init__(self, items=None, fields=None, item_count=0, field_count=0, flags=0):
        self.items = items
        self.fields = fields
        self.item_count = item_count
        self.field_count = field_count
        self.flags = flags

    @staticmethod
    def create():
        items = list()
        return RecordMap(items)

    def add(self, item):
        if self.flags & RecordFlags.IMMUTABLE.value:
            raise AttributeError('immutable')
        if self.flags & RecordFlags.ALIASED.value:
            return self.add_aliased(item)
        else:
            return self.add_mutable(item)

    def add_mutable(self, item):
        self.items.append(item)
        self.item_count = self.item_count + 1

        return True

    def add_aliased(self, item):
        pass

    @property
    def size(self):
        return self.item_count


class ValueBuilder:

    def __init__(self):
        self.record = None
        self.value = None
