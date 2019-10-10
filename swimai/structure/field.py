from abc import ABC, abstractmethod

from swimai.structure.item import Item


class Field(Item, ABC):

    @property
    @abstractmethod
    def key(self):
        ...

    @property
    @abstractmethod
    def value(self):
        ...
