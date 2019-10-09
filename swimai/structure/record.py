from abc import abstractmethod

from swimai.structure.item import Item
from swimai.structure.slot import Slot


class Record:

    @staticmethod
    def create(initial_size):
        return RecordMap.create(initial_size)

    @abstractmethod
    def add(self, item):
        pass

    def slot(self, key, value):
        self.add(Slot(key, value))
        return self


class RecordMap(Record):

    def __init__(self, items=None, fields=None, item_count=0, field_count=0):
        self.items = items
        self.fields = fields
        self.item_count = item_count
        self.field_count = field_count

    @staticmethod
    def create(initial_size):
        items = [Item() for _ in range(initial_size)]
        return RecordMap(items)

    def add(self, item):
        pass