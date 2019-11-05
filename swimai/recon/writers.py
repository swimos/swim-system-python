from abc import ABC, abstractmethod

from swimai.recon.utils import ReconUtils
from swimai.structures.structs import Field, Attr, Slot, Value, Record, Text, Absent, Num, Extant, Bool


class Writer(ABC):
    ...


class BlockWriter(Writer):

    @staticmethod
    async def write_item(item, writer):
        if isinstance(item, Field):
            return await writer.write_slot(await writer.key(item), await writer.value(item))
        else:
            return await writer.write_item(item)

    @staticmethod
    async def write_block(items, writer):
        return await BlockWriter.write(items, writer, first=True)

    @staticmethod
    async def write(items, writer, first, in_braces=False):
        output = ''

        for item in items:

            if isinstance(item, Attr):
                item_text = await writer.write_item(item)
            elif isinstance(item, Value) and not isinstance(item, Record):
                item_text = await writer.write_item(item)
            else:

                if not first:
                    output += ','
                elif isinstance(item, Slot):
                    if len(output) > 0 and output[-1] != '(':
                        output += '{'
                        in_braces = True

                item_text = await writer.write_item(item)

                first = False

            if item_text:
                output += item_text

        if in_braces:
            output += '}'

        return output


class ReconWriter(ABC):

    @abstractmethod
    async def write_value(self, value):
        ...

    @abstractmethod
    async def key(self, item):
        ...

    @abstractmethod
    async def value(self, item):
        ...

    async def is_ident(self, value):

        if len(value) == 0:
            return False

        if not await ReconUtils.is_ident_start_char(value[0]):
            return False

        for char in value:
            if not await ReconUtils.is_ident_char(char):
                return False

        return True

    async def write_attr(self, key, value):
        return await AttrWriter.write_attr(key, value, self)

    async def write_slot(self, key, value):
        return await SlotWriter.write_slot(key, value, self)

    async def write_text(self, value):
        if await self.is_ident(value):
            return await IdentWriter.write_ident(value)
        else:
            return await StringWriter.write_string(value)

    async def write_number(self, value):
        return await NumberWriter.write_number(value)

    async def write_bool(self, value):
        return await BoolWriter.write_bool(value)

    async def write_absent(self):
        pass

    async def write_record(self, record):
        if record.size > 0:
            return await BlockWriter.write_block(record.items, ReconStructureWriter())
        else:
            return '{}'


class ReconStructureWriter(ReconWriter):

    async def write_item(self, item):

        if isinstance(item, Field):
            if isinstance(item, Attr):
                return await self.write_attr(item.key, item.value)
            elif isinstance(item, Slot):
                return await self.write_slot(item.key, item.value)
        elif isinstance(item, Value):
            return await self.write_value(item)

        raise AttributeError(f'No Recon serialization for {item}')

    async def write_value(self, value):
        if isinstance(value, Record):
            return await self.write_record(value)
        elif isinstance(value, Text):
            return await self.write_text(value.get_string_value())
        elif isinstance(value, Num):
            return await self.write_number(value.get_num_value())
        elif isinstance(value, Bool):
            return await self.write_bool(value.get_bool_value())
        elif isinstance(value, Absent):
            return await self.write_absent()

    async def key(self, item):
        return item.key

    async def value(self, item):
        return item.value


class AttrWriter(Writer):

    @staticmethod
    async def write_attr(key, value, writer):

        output = '@'

        key_text = await writer.write_value(key)

        if key_text:
            output += key_text

        if value != Extant.get_extant():

            output += '('

            value_text = await writer.write_value(value)

            if value_text:
                output += value_text

            output += ')'

        return output


class SlotWriter(Writer):

    @staticmethod
    async def write_slot(key, value, writer):
        output = ''

        key_text = await writer.write_value(key)

        if key_text:
            output += key_text

        output += ':'

        value_text = await writer.write_value(value)

        if value_text:
            output += value_text

        return output


class StringWriter(Writer):

    @staticmethod
    async def write_string(value):
        output = '"'

        if value:
            output += value

        output += '"'

        return output


class NumberWriter(Writer):

    @staticmethod
    async def write_number(value):
        output = ''

        if value:
            output += str(value)

        return output


class BoolWriter(Writer):

    @staticmethod
    async def write_bool(value):

        if value:
            return 'true'
        else:
            return 'false'


class IdentWriter(Writer):

    @staticmethod
    async def write_ident(value):
        output = ''

        if value:
            output += value

        return output
