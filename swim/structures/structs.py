from abc import ABC, abstractmethod
from enum import Enum


class Item(ABC):

    @property
    @abstractmethod
    def key(self):
        ...

    def concat(self, new_item):

        record = Record.create()
        record.add(self)

        if isinstance(new_item, Record):
            record.add_all(new_item.items)
        else:
            record.add(new_item)

        return record

    @staticmethod
    def from_object(obj):
        if isinstance(obj, Item):
            return obj
        elif isinstance(obj, dict):
            entry = next(iter(obj.items()))
            return Slot.of(entry[0], entry[1])
        else:
            return Value.from_object(obj)

    @staticmethod
    def extant():
        return Extant.get_extant()

    @staticmethod
    def absent():
        return Absent.get_absent()


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

        if isinstance(key, Text):
            return Attr(key, value)
        elif isinstance(key, str):
            return Attr(Text.create_from(key), value)
        else:
            raise TypeError('key')

    def key_equals(self, item):
        if isinstance(item, str):
            return self.key.value == item
        elif isinstance(item, Field):
            return self.key == item.key
        else:
            return self.key == item


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
    def create_from(string):
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

    def float_value(self):
        return float(self.value)


class Num(Value):

    def __init__(self, value):
        self.value = value

    @staticmethod
    def create_from(value):
        return Num(value)

    def num_value(self):
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


class Extant(Value):
    extant = None

    @staticmethod
    def get_extant():
        if Extant.extant is None:
            Extant.extant = Extant()

        return Extant()


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

    @staticmethod
    def of(key, value=None):
        if key is None:
            raise Exception('Key is empty!')

        if value is None:
            value = Value.extant()

        return Slot(key, value)


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
            key = Text.create_from(key)

        if isinstance(value, str):
            value = Text.create_from(value)

        self.add(Slot(key, value))
        return self

    @property
    @abstractmethod
    def size(self):
        ...

    def length(self):
        return self.size

    def get_headers(self, tag):
        head = self.get_head()

        if isinstance(head, Attr) and head.key_equals(tag):
            header = head.value
            if isinstance(header, Record):
                return header
            else:
                return RecordMap.of(header)
        else:
            return None

    def get_head(self):
        return self.get_item(0)

    @abstractmethod
    def get_item(self, index):
        ...

    def bind(self):
        return self


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

        if isinstance(item, Field):
            self.field_count += 1

        return True

    def add_aliased(self, item):
        pass

    @property
    def size(self):
        return self.item_count

    @property
    def tag(self):
        if self.field_count > 0:
            item = self.items[0]
            if isinstance(item, Attr):
                return item.key.value

        return None

    def get_item(self, index):
        if 0 <= index < self.item_count:
            return self.items[index]
        else:
            return Item.absent()

    def get_body(self):
        n = self.item_count

        if n > 2:
            return RecordMapView(self, 1, n).branch()
        elif n == 2:
            item = self.items[1]

            if isinstance(item, Value):
                return item
            else:
                return RecordMap.of(item)

        else:
            return Value.absent()

    @staticmethod
    def of(obj):
        array = list()
        item = Item.from_object(obj)
        array.append(item)

        field_count = 1 if isinstance(item, Field) else 0

        return RecordMap(array, None, 1, field_count, 0)


class RecordMapView(Record):

    def __init__(self, record, lower, upper):
        self.record = record
        self.lower = lower
        self.upper = upper

    def add(self, item):
        pass

    @property
    def size(self):
        return self.upper - self.lower

    def get_item(self, index):
        pass

    def branch(self):
        size = self.size
        fields_count = 0
        copy_index = self.lower
        new_array = list()

        for _ in range(0, size):

            item = self.record.items[copy_index]
            new_array.append(item)

            if isinstance(item, Field):
                fields_count += 1

            copy_index += 1

        return RecordMap(new_array, None, size, fields_count, 0)


class ValueBuilder:

    def __init__(self):
        self.record = None
        self.value = None

    def add(self, item):

        if isinstance(item, Field):
            return self.add_field(item)
        elif isinstance(item, Value):
            return self.add_value(item)
        else:
            raise AssertionError(item)

    def add_field(self, item):
        if self.record is None:
            self.record = Record.create()

            if self.value is not None:
                self.record.add(self.value)
                self.value = None

        self.record.add(item)
        return True

    def add_value(self, item):
        if self.record is not None:
            self.record.add(item)
        elif self.value is None:
            self.value = item
        else:
            self.record = Record.create()
            self.record.add(self.value)
            self.value = None
            self.record.add(item)

        return True

    def bind(self):
        if self.record is not None:
            return self.record
        elif self.value is not None:
            return self.value
        else:
            return Value.absent()
