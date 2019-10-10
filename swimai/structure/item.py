from abc import ABC, abstractmethod

from swimai.structure.extant import Extant
from swimai.structure.record import Record


class Item(ABC):

    @property
    @abstractmethod
    def key(self):
        ...

    @staticmethod
    def extant():
        return Extant.extant()

    def concat(self, new_item):

        record = Record.create()
        record.add(self)

        if isinstance(new_item, Record):
            record.add_all(new_item)
        else:
            record.add(new_item)

        return record
