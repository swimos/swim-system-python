from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, List, Optional, Dict


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
    def create_from(obj: Any) -> 'Item':
        """
        Create Item object from a compatible object.

        :param obj:             - Object extending Item or a dictionary.
        :return:                - Converted object as Item.
        """
        if isinstance(obj, Item):
            return obj
        elif isinstance(obj, dict) and len(obj) == 1:
            entry = next(iter(obj.items()))
            return Slot.create_slot(entry[0], entry[1])
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

    @property
    @abstractmethod
    def key(self) -> 'Any':
        ...

    @property
    @abstractmethod
    def value(self) -> 'Any':
        ...


class Field(Item):

    @property
    @abstractmethod
    def key(self) -> 'Any':
        ...

    @property
    @abstractmethod
    def value(self) -> Any:
        ...


class Attr(Field):

    def __init__(self, key: 'Value', value: Any) -> None:
        self.__key = key
        self.__value = value

    @property
    def key(self) -> 'Value':
        return self.__key

    @property
    def value(self) -> Any:
        return self.__value

    @staticmethod
    def create_attr(key: Any, value: Any) -> 'Attr':
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

    def key_equals(self, item: Any) -> bool:
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
    def size(self) -> int:
        return 0

    @staticmethod
    def create_from(obj: Any) -> 'Value':
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

    def __init__(self, value: (int, float)) -> None:
        self.__value = value

    @property
    def value(self) -> (int, float):
        return self.__value

    @staticmethod
    def create_from(obj: (float, int)) -> 'Num':
        """
        Create Num object from a compatible object.

        :param obj:             - Integer or Float value.
        :return:                - Converted value as a Num object.
        """

        return Num(obj)

    def get_num_value(self) -> (int, float):
        """
        Return the value of the Num object as integer or float.

        :return:                - Num value as integer or float.
        """
        return self.value


class Bool(Value):
    TRUE = None
    FALSE = None

    def __init__(self, value: bool) -> None:
        self.__value = value

    @property
    def value(self) -> bool:
        return self.__value

    @staticmethod
    def create_from(obj: bool) -> 'Bool':
        """
        Create Bool object from a compatible object.

        :param obj:             - Boolean value.
        :return:                - Converted value as a Bool object.
        """

        if obj:
            if Bool.TRUE is None:
                Bool.TRUE = Bool(True)

            return Bool.TRUE
        else:
            if Bool.FALSE is None:
                Bool.FALSE = Bool(False)

            return Bool.FALSE

    def get_bool_value(self) -> bool:
        """
        Return the value of the Bool object as Boolean.

        :return:                - Bool value as Boolean.
        """
        return self.value


class Absent(Value):
    absent = None

    @staticmethod
    def get_absent() -> 'Absent':
        """
        Create an Absent singleton if it does not exist and return it

        :return:                - Absent singleton.
        """
        if Absent.absent is None:
            Absent.absent = Absent()

        return Absent.absent


class Extant(Value):
    extant = None

    @staticmethod
    def get_extant() -> 'Extant':
        """
        Create an Extant singleton if it does not exist and return it

        :return:                - Extant singleton.
        """
        if Extant.extant is None:
            Extant.extant = Extant()

        return Extant.extant


class Slot(Field):

    def __init__(self, key: Any, value: Any = Value.extant()) -> None:
        self.__key = key
        self.__value = value

    @property
    def key(self) -> Any:
        return self.__key

    @property
    def value(self) -> Any:
        return self.__value

    @staticmethod
    def create_slot(key: Any, value: Any = None) -> 'Slot':
        """
        Create a slot object from given key and value (optional).

        :param key:             - Key for the slot.
        :param value:           - Value for the slot. Defaults to Extant.
        :return:                - Slot object.
        """

        if key is None:
            raise TypeError('Empty key for slot!')

        if value is None:
            value = Value.extant()

        return Slot(key, value)


class RecordFlags(Enum):
    """
    IMMUTABLE(1), ALIASED(2)
    """
    IMMUTABLE = 1 << 0
    ALIASED = 1 << 1


class Record(Value):

    @property
    def size(self) -> int:
        return self.size

    @abstractmethod
    def add(self, item) -> bool:
        ...

    @abstractmethod
    def get_item(self, index: int) -> 'Value':
        """

        :param index:
        :return:
        """
        ...

    @abstractmethod
    def get_items(self) -> List['Value']:
        """

        :return:
        """
        ...

    @staticmethod
    def create() -> 'RecordMap':
        """

        :return:
        """
        return RecordMap.create()

    def add_all(self, items: List['Value']) -> bool:
        """

        :param items:
        :return:
        """
        changed = False

        for item in items:
            self.add(item)
            changed = True

        return changed

    def add_slot(self, key: Any, value: Any) -> 'Record':
        """

        :param key:
        :param value:
        :return:
        """
        if isinstance(key, str):
            key = Text.create_from(key)

        if isinstance(value, str):
            value = Text.create_from(value)

        self.add(Slot.create_slot(key, value))

        return self

    def get_headers(self, tag: str) -> Optional['Record']:
        """

        :param tag:
        :return:
        """
        head = self.get_head()

        if isinstance(head, Attr) and head.key_equals(tag):
            header = head.value
            if isinstance(header, Record):
                return header
            else:
                return RecordMap.create_record_map(header)
        else:
            return None

    def get_head(self) -> 'Item':
        """

        :return:
        """
        return self.get_item(0)

    def bind(self) -> 'Record':
        """

        :return:
        """
        return self


class RecordMap(Record):

    def __init__(self, items: List[Item] = None, fields: Dict[str, Item] = None, item_count: int = 0, field_count: int = 0, flags: int = 0) -> None:
        self.items = items
        self.fields = fields
        self.item_count = item_count
        self.field_count = field_count
        self.flags = flags

    def get_items(self) -> List[Item]:
        return self.items

    @staticmethod
    def create() -> 'RecordMap':
        """

        :return:
        """
        items = list()
        return RecordMap(items, flags=RecordFlags.ALIASED.value)

    def add(self, item: Item) -> bool:
        """

        :param item:
        :return:
        """
        if self.flags & RecordFlags.IMMUTABLE.value:
            raise TypeError('Cannot add item to immutable record!')
        if self.flags & RecordFlags.ALIASED.value:
            return self.add_aliased(item)
        else:
            return self.add_mutable(item)

    def add_mutable(self, item: Item) -> bool:
        """

        :param item:
        :return:
        """
        self.items = self.items[:]
        self.items.append(item)
        self.item_count = self.item_count + 1

        if isinstance(item, Field):
            self.field_count += 1

            if self.fields is not None and self.fields.lengt > self.item_count:
                self.fields[item.key.value] = item
            else:
                self.fields = None

        return True

    def add_aliased(self, item: Item) -> bool:
        """

        :param item:
        :return:
        """
        self.items = self.items[:]
        self.items.append(item)
        self.item_count = self.item_count + 1

        if isinstance(item, Field):
            self.field_count += 1

        self.fields = None
        self.flags &= ~RecordFlags.ALIASED.value
        return True

    def commit(self) -> 'RecordMap':
        """

        :return:
        """
        self.flags |= RecordFlags.IMMUTABLE.value
        return self

    def contains_key(self, key: Any) -> bool:
        """

        :param key:
        :return:
        """
        if not isinstance(key, (Value, str)):
            key = Value.create_from(key)

        if self.field_count != 0:
            self.__init_hash_table()

            return key in self.fields

        return False

    def branch(self) -> 'RecordMap':
        """

        :return:
        """
        self.flags |= RecordFlags.ALIASED.value
        return RecordMap(self.items, self.fields, self.item_count, self.field_count, RecordFlags.ALIASED.value)

    def __init_hash_table(self) -> None:
        """

        :return:
        """
        self.fields = dict()
        for item in self.items:
            self.fields[item.key.value] = item

    @property
    def size(self) -> int:
        return self.item_count

    @property
    def tag(self) -> Optional[str]:
        """

        :return:
        """
        if self.field_count > 0:
            item = self.items[0]
            if isinstance(item, Attr):
                return str(item.key.value)

        return None

    def get_item(self, index: int) -> Item:
        """

        :param index:
        :return:
        """
        if 0 <= index < self.item_count:
            return self.items[index]
        else:
            return Item.absent()

    def get_body(self) -> Item:
        """

        :return:
        """
        n = self.item_count

        if n > 2:
            return RecordMapView(self, 1, n).branch()
        elif n == 2:
            item = self.items[1]

            if isinstance(item, Value):
                return item
            else:
                return RecordMap.create_record_map(item)

        else:
            return Value.absent()

    @staticmethod
    def create_record_map(obj: Any) -> 'RecordMap':
        """

        :param obj:
        :return:
        """
        array = list()
        item = Item.create_from(obj)
        array.append(item)

        field_count = 1 if isinstance(item, Field) else 0

        return RecordMap(array, None, 1, field_count, 0)


class RecordMapView(Record):

    def __init__(self, record: RecordMap, lower: int, upper: int) -> None:
        self.record = record
        self.lower = lower
        self.upper = upper

    def add(self, item: Item, index: int = None) -> bool:
        """

        :param item:
        :param index:
        :return:
        """
        if index is None:
            index = self.size

        if self.record.flags & RecordFlags.IMMUTABLE.value:
            raise TypeError('Cannot add item to immutable record!')
        elif index < 0 or index > self.size:
            raise IndexError(f'Index {index} is out of range!')
        else:
            self.add_item(index, item)

        return True

    def add_item(self, index: int, item: Item) -> None:
        """

        :param index:
        :param item:
        :return:
        """
        lower = self.lower + index
        self.record.items = self.record.items[0: lower] + [item] + self.record.items[lower: self.record.size - lower]
        self.record.fields = None
        self.record.item_count += 1

        if isinstance(item, Field):
            self.record.field_count += 1

        self.record.flags = self.record.flags & ~RecordFlags.ALIASED.value
        self.upper += 1

    @property
    def size(self) -> int:
        return self.upper - self.lower

    def get_item(self, index: int) -> Item:
        """

        :param index:
        :return:
        """
        if 0 <= index < self.size:
            return self.record.items[self.lower + index]
        else:
            return Item.absent()

    def get_items(self) -> List[Item]:
        """

        :return:
        """
        return self.record.items[self.lower: self.upper]

    def branch(self) -> RecordMap:
        """

        :return:
        """
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

    def __init__(self) -> None:
        self.record = None
        self.value = None

    def add(self, item: Item) -> bool:
        """

        :param item:
        :return:
        """
        if isinstance(item, Field):
            return self.add_field(item)
        elif isinstance(item, Value):
            return self.add_value(item)
        else:
            raise AssertionError(item)

    def add_field(self, item: Field) -> bool:
        """

        :param item:
        :return:
        """
        if self.record is None:
            self.record = Record.create()

            if self.value is not None:
                self.record.add(self.value)
                self.value = None

        self.record.add(item)
        return True

    def add_value(self, item: Value) -> bool:
        """

        :param item:
        :return:
        """
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

    def bind(self) -> Value:
        """

        :return:
        """
        if self.record is not None:
            return self.record
        elif self.value is not None:
            return self.value
        else:
            return Value.absent()
