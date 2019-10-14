from abc import ABC, abstractmethod

from swimai.structure.structs import Field, Attr, Slot, Value, Record, Text, Absent, RecordMap


class Writer:
    pass
    # @staticmethod
    # async def write(items, writer):
    #     if isinstance(items, Field):
    #         writer.write_slot(writer.key(items))
    #     else:
    #
    #         wrt
    #
    #         output_list = list()
    #         for item in items:
    #             output = await writer.write_item(item)
    #             if output:
    #                 output_list.append(output)
    #
    #         return ','.join(output_list)


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
    async def write(items, writer, first):
        # TODO make this more clear
        output = ''

        for item in items:

            if isinstance(item, Attr):
                item_text = await writer.write_item(item)
            elif isinstance(item, Value) and not isinstance(item, Record):
                item_text = await writer.write_item(item)
            else:

                if not first:
                    output += ','
                item_text = await writer.write_item(item)

                first = False

            if item_text:
                output += item_text

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

        if not await Recon.is_ident_start_char(ord(value[0])):
            return False

        for char in value:
            if not await Recon.is_ident_char(ord(char)):
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

        # TODO add exception
        return f'No Recon serialization for {item}'

    async def write_value(self, value):
        if isinstance(value, Record):
            return await self.write_record(value)
        elif isinstance(value, Text):
            return await self.write_text(value.string_value())
        elif isinstance(value, Absent):
            return await self.write_absent()

    async def key(self, item):
        return item.key

    async def value(self, item):
        return item.value


class Recon:
    structure_writer = None

    @staticmethod
    def parse(string):
        """
        Parse a string and return Value object.
        :param string:
        :return:
        """
        pass

    @staticmethod
    async def to_string(item):
        """
        Parse an Item object to string.
        :return:
        """
        return await Recon.write(item)

    @staticmethod
    async def write(item):
        return await Recon.get_structure_writer().write_item(item)

    @staticmethod
    def get_structure_writer():
        if Recon.structure_writer is None:
            Recon.structure_writer = ReconStructureWriter()

        return Recon.structure_writer

    @staticmethod
    async def is_ident_start_char(c):
        return ord('A') <= c <= ord('Z') or c == ord('_') or ord('a') <= c <= ord(
            'z') or 0xc0 <= c <= 0xd6 or 0xd8 <= c <= 0xf6 or 0xf8 <= c <= 0x2ff or 0x370 <= c <= 0x37d or 0x37f <= c <= 0x1fff or 0x200c <= c <= 0x200d or 0x2070 <= c <= 0x218f or 0x2c00 <= c <= 0x2fef or 0x3001 <= c <= 0xd7ff or 0xf900 <= c <= 0xfdcf or 0xfdf0 <= c <= 0xfffd or 0x10000 <= c <= 0xeffff

    @staticmethod
    async def is_ident_char(c):
        return c == ord('-') or ord('0') <= c <= ord('9') or ord('A') <= c <= ord('Z') or c == ord('_') or ord('a') <= c <= ord(
            'z') or c == 0xb7 or 0xc0 <= c <= 0xd6 or 0xd8 <= c <= 0xf6 or 0xf8 <= c <= 0x37d or 0x37f <= c <= 0x1fff or 0x200c <= c <= 0x200d or 0x203f <= c <= 0x2040 or 0x2070 <= c <= 0x218f or 0x2c00 <= c <= 0x2fef or 0x3001 <= c <= 0xd7ff or 0xf900 <= c <= 0xfdcf or 0xfdf0 <= c <= 0xfffd or 0x10000 <= c <= 0xeffff


class AttrWriter(Writer):

    @staticmethod
    async def write_attr(key, value, writer):

        # TODO change this
        output = ''
        output += '@'

        key_text = await writer.write_value(key)

        if key_text:
            output += key_text

        output += '('

        value_text = await writer.write_value(value)

        if value_text:
            output += value_text

        output += ')'

        return output


class SlotWriter(Writer):

    @staticmethod
    async def write_slot(key, value, writer):
        # TODO change this
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
        # TODO change this
        output = '"'

        if value:
            output += value

        output += '"'

        return output


class IdentWriter(Writer):

    @staticmethod
    async def write_ident(value):
        # TODO change this
        output = ''

        if value:
            output += value

        return output
