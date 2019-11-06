from abc import ABC, abstractmethod

from swimai.recon.utils import ReconUtils, OutputMessage
from swimai.structures.structs import Field, Attr, Slot, Value, Record, Text, Absent, Num, Extant, Bool


class ReconWriter:

    @staticmethod
    async def write_text(value):
        if await ReconUtils.is_ident(value):
            return await IdentWriter.write(value=value)
        else:
            return await StringWriter.write(value=value)

    @staticmethod
    async def write_number(value):
        return await NumberWriter.write(value=value)

    @staticmethod
    async def write_bool(value):
        return await BoolWriter.write(value=value)

    async def write_item(self, item):

        if isinstance(item, Field):
            if isinstance(item, Attr):
                return await self.write_attr(item.key, item.value)
            elif isinstance(item, Slot):
                return await self.write_slot(item.key, item.value)
        elif isinstance(item, Value):
            return await self.write_value(item)

        raise AttributeError(f'No Recon serialization for {item}')

    async def write_attr(self, key, value):
        return await AttrWriter.write(key=key, value=value, writer=self)

    async def write_slot(self, key, value):
        return await SlotWriter.write(key=key, writer=self, value=value)

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

    async def write_record(self, record):
        if record.size > 0:
            return await BlockWriter.write(items=record.items, writer=self, first=True)
        else:
            return OutputMessage.create('{}')

    async def write_absent(self):
        # no-op
        pass


class Writer(ABC):
    @staticmethod
    @abstractmethod
    async def write():
        ...


class BlockWriter(Writer):

    @staticmethod
    async def write(items=None, writer=None, first=None, in_braces=False):
        output = await OutputMessage.create()

        for item in items:

            if isinstance(item, Attr):
                item_text = await writer.write_item(item)
            elif isinstance(item, Value) and not isinstance(item, Record):
                item_text = await writer.write_item(item)
            else:
                if not first:
                    await output.append(',')
                elif isinstance(item, Slot):
                    if output.size > 0 and output.last_char != '(':
                        await output.append('{')
                        in_braces = True

                item_text = await writer.write_item(item)

                first = False

            if item_text:
                await output.append(item_text)

        if in_braces:
            await output.append('}')

        return output.value


class AttrWriter(Writer):

    @staticmethod
    async def write(key=None, writer=None, value=None):

        output = await OutputMessage.create('@')

        key_text = await writer.write_value(key)

        if key_text:
            await output.append(key_text)

        if value != Extant.get_extant():

            await output.append('(')

            value_text = await writer.write_value(value)

            if value_text:
                await output.append(value_text)

            await output.append(')')

        return output


class SlotWriter(Writer):

    @staticmethod
    async def write(key=None, writer=None, value=None):
        output = await OutputMessage.create()

        key_text = await writer.write_value(key)

        if key_text:
            await output.append(key_text)

        await output.append(':')

        value_text = await writer.write_value(value)

        if value_text:
            await output.append(value_text)

        return output


class StringWriter(Writer):

    @staticmethod
    async def write(value=None):
        output = await OutputMessage.create('"')

        if value:
            await output.append(value)

        await output.append('"')

        return output


class NumberWriter(Writer):

    @staticmethod
    async def write(value=None):
        output = await OutputMessage().create()

        if value:
            await output.append(value)

        return output


class BoolWriter(Writer):

    @staticmethod
    async def write(value=None):

        if value:
            return await OutputMessage.create('true')
        else:
            return await OutputMessage.create('false')


class IdentWriter(Writer):

    @staticmethod
    async def write(value=None):
        output = await OutputMessage.create()

        if value:
            await output.append(value)

        return output
