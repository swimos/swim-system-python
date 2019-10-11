from enum import Enum
from abc import abstractmethod, ABC

from swimai.structure.slot import Slot
from swimai.structure.value import Value, Text


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
