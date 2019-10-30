from abc import ABC, abstractmethod
from enum import Enum


class Item(ABC):

    def concat(self, new_item: 'Item') -> 'Record':
        """
        Creates a Record object by appending an Item object to the current Item.

        :param new_item:        - New Item to add to the Record.
        :return:                - Record containing the current Item and the new Item.
        """
        record = Record.create()
        record.add(self)

        if isinstance(new_item, Record):
            record.add_all(new_item.get_items())
        else:
            record.add(new_item)

        return record

    @staticmethod
    def create_from(obj: object) -> 'Item':
        """
        Create Item object from a compatible object.

        :param obj:             - Object extending Item or a dictionary.
        :return:                - Converted object as Item.
        """
        if isinstance(obj, Item):
            return obj
        elif isinstance(obj, dict) and len(obj) == 1:
            entry = next(iter(obj.items()))
            return Slot.of(entry[0], entry[1])
        else:
            return Value.create_from(obj)

    @staticmethod
    def extant() -> 'Extant':
        """
        Return Extant item singleton.

        :return:                - Item of type Extant.
        """
        return Extant.get_extant()

    @staticmethod
    def absent() -> 'Absent':
        """
        Return Absent item singleton.

        :return:                - Item of type Absent.
        """
        return Absent.get_absent()


class Field(Item):

    @property
    @abstractmethod
    def key(self) -> 'Value':
        ...

    @property
    @abstractmethod
    def value(self) -> object:
        ...


class Attr(Field):

    def __init__(self, key: 'Value', value: object) -> None:
        self.__key = key
        self.__value = value

    @property
    def key(self) -> 'Value':
        return self.__key

    @property
    def value(self) -> object:
        return self.__value

    @staticmethod
    def create_attr(key: object, value: object) -> 'Attr':
        """
        Create an attribute object from given key and value.

        :param key:             - Key of the attribute. Can be Text or str.
        :param value:           - Value of the attribute.
        :return:                - Attribute object.
        """
        if key is None:
            raise TypeError('Empty key for attribute!')

        if value is None:
            raise TypeError('Empty value for attribute!')

        if isinstance(key, Text):
            return Attr(key, value)
        elif isinstance(key, str):
            return Attr(Text.create_from(key), value)
        else:
            raise TypeError(f'Invalid key: {key}')

    def key_equals(self, item: object) -> bool:
        """
        Compare the key of the attribute to an arbitrary object.

        :param item:            - Item to compare the key to.
        :return:                - True if the key and the item are equal, False otherwise.
        """
        if isinstance(item, str):
            return self.key.value == item
        elif isinstance(item, Field):
            return self.key.value == item.key.value
        else:
            return self.key.value == item


class Value(Item):

    @property
    def key(self) -> 'Value':
        return Value.absent()

    @property
    def value(self) -> 'Value':
        return Value.absent()

    @property
    def length(self) -> int:
        return 0

    @staticmethod
    def create_from(obj: object) -> 'Value':
        """
        Create Value object from a compatible object.

        :param obj:             - Object extending Value or None.
        :return:                - Converted object as Value.
        """

        if obj is None:
            return Extant.get_extant()
        elif isinstance(obj, Value):
            return obj
        elif isinstance(obj, str):
            return Text.create_from(obj)
        elif isinstance(obj, (float, int)):
            return Num.create_from(obj)
        elif isinstance(obj, bool):
            return Bool.create_from(obj)
        else:
            raise TypeError(f'{str(obj)} cannot be converted to Value!')


class Text(Value):
    empty = None

    def __init__(self, value: str) -> None:
        self.__value = value

    @property
    def value(self) -> str:
        return self.__value

    @staticmethod
    def create_from(string: str) -> 'Text':
        """
        Create Text object from a string.

        :param string:          - String value.
        :return:                - Converted string as a Text object.
        """
        if not string:
            return Text.get_empty()
        return Text(string)

    @staticmethod
    def get_empty() -> 'Text':
        """
        Create an empty Text singleton if it does not exist and return it.

        :return:                - Empty Text singleton.
        """
        if Text.empty is None:
            Text.empty = Text('')

        return Text.empty

    def get_string_value(self) -> str:
        """
        Return the value of the Text object as string.

        :return:                - Text value as string.
        """
        return self.value


class Num(Value):

    def __init__(self, value):
        self.__value = value

    @property
    def value(self):
        return self.__value

    @staticmethod
    def create_from(value):
        return Num(value)

    def num_value(self):
        return self.value


class Bool(Value):
    TRUE = None
    FALSE = None

    def __init__(self, value):
        self.__value = value

    @property
    def value(self):
        return self.__value

    @staticmethod
    def create_from(value):

        if value:
            if Bool.TRUE is None:
                Bool.TRUE = Bool(True)

            return Bool.TRUE
        else:
            if Bool.FALSE is None:
                Bool.FALSE = Bool(False)

            return Bool.FALSE

    def bool_value(self):
        return self.value


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

        return Extant.extant


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


class Record(Value):

    @staticmethod
    def create():
        return RecordMap.create()

    @abstractmethod
    def add(self, item):
        ...

    @abstractmethod
    def get_items(self):
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

    @property
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

    def get_items(self):
        return self.items

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
        item = Item.create_from(obj)
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

    def get_items(self):
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
