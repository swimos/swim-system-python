from abc import ABC, abstractmethod

from swimai.structure.structs import Field, Attr, Slot, Value, Record, Text, Absent


class Writer:
    @staticmethod
    async def write(items, writer):
        if isinstance(items, Field):
            writer.write_slot(writer.key(items))
        else:
            output_list = list()
            for item in items:
                output = await writer.write_item(item)
                if output:
                    output_list.append(output)

            return ','.join(output_list)


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

    async def write_attr(self, key, value):
        return await AttrWriter.write_attr(key, value, self)

    async def write_slot(self, key, value):
        return await SlotWriter.write_slot(key, value, self)

    async def write_text(self, value):
        return await StringWriter.write_string(value)

    async def write_absent(self):
        pass

    async def write_record(self, record):
        if record.size > 0:
            return await Writer.write(record.items, self)
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

        output += '"'
        value_text = await writer.write_value(value)

        if value_text:
            output += value_text

        output += '"'
        return output


class StringWriter(Writer):

    @staticmethod
    async def write_string(value):
        # TODO change this
        output = ''

        if value:
            output += value

        return output
