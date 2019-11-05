from abc import ABC, abstractmethod

from swimai.recon.utils import ReconUtils
from swimai.structures.structs import ValueBuilder, Text, Bool, Attr, Value, Record, Slot, Num


class ReconParser:

    @staticmethod
    async def create_ident(value):
        if isinstance(value, str):
            if value == 'true':
                return Bool.create_from(True)
            elif value == 'false':
                return Bool.create_from(False)

        return Text.create_from(value)

    @staticmethod
    async def create_attr(key, value=Value.extant()):
        return Attr.create_attr(key, value)

    @staticmethod
    async def create_record_builder():
        return Record.create()

    @staticmethod
    async def create_value_builder():
        return ValueBuilder()

    @staticmethod
    async def create_slot(key, value=None):
        return Slot.create_slot(key, value)

    @staticmethod
    async def create_number(value):
        return Num.create_from(value)

    async def parse_block_string(self, recon_string):
        message = InputMessage(recon_string)
        return await self.parse_block(message)

    async def parse_block(self, message):
        return await BlockParser.parse(message=message, parser=self)

    async def parse_block_expression(self, message):
        return await self.parse_attr_expression(message)

    async def parse_record(self, message, builder):
        return await RecordParser.parse(message=message, parser=self, builder=builder)

    async def parse_attr_expression(self, message, builder=None):
        return await AttrExpressionParser.parse(message=message, parser=self, builder=builder)

    async def parse_attr(self, message):
        return await AttrParser.parse(message=message, parser=self)

    async def parse_string(self, message):
        return await StringParser.parse(message=message, parser=self)

    async def parse_number(self, message):
        return await NumberParser.parse(message=message, parser=self)

    async def parse_literal(self, message, builder=None):
        return await LiteralParser.parse(message=message, parser=self, builder=builder)

    async def parse_ident(self, message):
        return await IdentParser.parse(message=message, parser=self)


class Parser(ABC):
    @staticmethod
    @abstractmethod
    async def parse():
        ...


class BlockParser(Parser):

    @staticmethod
    async def parse(message=None, parser=None, builder=None, key_output=None, value_output=None):

        char = message.head()

        while await ReconUtils.is_space(char):
            char = message.step()

        if builder is None:
            builder = await parser.create_value_builder()

        if key_output is None:
            key_output = await parser.parse_block_expression(message)

        char = message.head()

        while await ReconUtils.is_space(char):
            char = message.step()

        if message.is_cont():

            if char == ':':
                char = message.step()

            while await ReconUtils.is_space(char):
                char = message.step()

            if value_output is None:
                value_output = await parser.parse_block_expression(message)

            builder.add(await parser.create_slot(key_output, value_output))

            char = message.head()
            if char == ',' or char == ';':
                message.step()
                await BlockParser.parse(message, parser, builder)

            return builder.bind()

        else:
            builder.add(key_output)
            return builder.bind()


class RecordParser(Parser):

    @staticmethod
    async def parse(message=None, parser=None, builder=None, key_output=None, value_output=None):
        char = message.head()

        if char == '{':
            char = message.step()

        while await ReconUtils.is_space(char):
            char = message.step()

        if key_output is None:
            key_output = await parser.parse_block_expression(message)

        while await ReconUtils.is_space(char):
            char = message.step()

        if message.is_cont():
            if message.head() == ':':
                message.step()

                if value_output is None:
                    value_output = await parser.parse_block_expression(message)

                builder.add(await parser.create_slot(key_output, value_output))

            else:
                builder.add(key_output)

        if message.is_cont():
            char = message.head()

            if char == ',' or char == ';':
                message.step()
                await RecordParser.parse(message, parser, builder)

            elif char == '}':
                message.step()
                return builder


class AttrExpressionParser(Parser):

    @staticmethod
    async def parse(message=None, parser=None, builder=None, field_output=None, value_output=None):

        char = message.head()

        while await ReconUtils.is_space(char):
            char = message.step()

        if char == '@':
            if field_output is None:
                field_output = await parser.parse_attr(message)

            if builder is None:
                builder = await parser.create_record_builder()

            builder.add(field_output)

            await AttrExpressionParser.parse(message, parser, builder)

            return builder

        elif await ReconUtils.is_ident_start_char(char) or char == '"' or await ReconUtils.is_digit(char) or char == '-':
            if value_output is None:
                value_output = await parser.parse_literal(message)

            if builder is None:
                builder = await parser.create_value_builder()

            builder.add(value_output)
            return builder.bind()

        elif char == '{' or char == '[':
            if builder is None:
                builder = await parser.create_record_builder()

            if value_output is None:
                await parser.parse_literal(message, builder)

            if message.is_cont():
                if message.head() == '@':
                    await AttrExpressionParser.parse(message, parser, builder)


class AttrParser(Parser):

    @staticmethod
    async def parse(message=None, parser=None, key_output=None, value_output=None):

        char = message.head()
        if char == '@':
            char = message.step()

            if char == '"':
                if key_output is None:
                    key_output = await parser.parse_string(message)
            else:

                if key_output is None:
                    key_output = await parser.parse_ident(message)

                if message.head() == '(' and message.is_cont():
                    message.step()
                else:
                    return await parser.create_attr(key_output)

                if message.head() == ')':
                    message.step()
                    return await parser.create_attr(key_output)
                else:
                    if value_output is None:
                        value_output = await parser.parse_block(message)

                if message.head() == ')':
                    message.step()
                    return await parser.create_attr(key_output, value_output)

        return await parser.create_attr(key_output, value_output)


class IdentParser(Parser):

    @staticmethod
    async def parse(message=None, parser=None, output=None):

        char = message.head()

        if await ReconUtils.is_ident_start_char(char):
            if output is None:
                output = ''

            output = output + char
            char = message.step()

            while await ReconUtils.is_ident_char(char):
                output = output + char
                char = message.step()

        return await parser.create_ident(output)


class StringParser(Parser):

    @staticmethod
    async def parse(message=None, parser=None, output=None):
        char = message.head()

        while await ReconUtils.is_space(char):
            char = message.step()

        if char == '"':

            if output is None:
                output = ''

            char = message.step()

            while char != '"' and message.is_cont():
                output = output + char
                char = message.step()

            message.step()

        return Text.create_from(output)


class NumberParser(Parser):

    @staticmethod
    async def parse(message=None, parser=None, value_output=None, sign_output=1):

        char = message.head()

        if char == '-':
            sign_output = -1
            char = message.step()

        if char == '0':
            char = message.step()
        elif '1' <= char <= '9':
            value_output = sign_output * int(char)
            char = message.step()

            while message.is_cont() and await ReconUtils.is_digit(char):
                value_output = 10 * value_output + sign_output * int(char)
                char = message.step()

        if message.is_cont():
            if char == '.':
                return await DecimalParser.parse(message, parser, value_output, sign_output)
            else:
                return await parser.create_number(value_output)
        else:
            return await parser.create_number(value_output)


class DecimalParser(Parser):

    @staticmethod
    async def parse(message=None, parser=None, value_output=None, sign_output=None):
        builder = ''

        if sign_output < 0 and value_output is None:
            builder += '-0'
        else:
            if value_output is None:
                value_output = 0

            builder += str(value_output)

        char = message.head()

        if char == '.':
            builder += '.'
            message.step()

            if message.is_cont():
                char = message.head()

                if await ReconUtils.is_digit(char):
                    builder += char
                    char = message.step()

                while message.is_cont() and await ReconUtils.is_digit(char):
                    builder += char
                    char = message.step()

                return await parser.create_number(float(builder))


class LiteralParser(Parser):

    @staticmethod
    async def parse(message=None, parser=None, value_output=None, builder=None):
        char = message.head()

        if char == '(':
            pass
        elif char == '{':
            if builder is None:
                builder = await parser.create_record_builder()

            await parser.parse_record(message, builder)

        elif char == '[':
            pass
        elif await ReconUtils.is_ident_start_char(char):
            value_output = await parser.parse_ident(message)
        elif char == '"':
            value_output = await parser.parse_string(message)
        elif char == '-' or await ReconUtils.is_digit(char):
            value_output = await parser.parse_number(message)
        if builder is None:
            builder = await parser.create_value_builder()

        if value_output is not None:
            builder.add(value_output)

        return builder.bind()


class InputMessage:

    def __init__(self, message):
        self.message = message
        self.index = 0

    def head(self):

        if self.is_cont():
            return self.message[self.index]
        else:
            return ''

    def step(self):
        self.index = self.index + 1
        return self.head()

    def is_cont(self):
        if self.index >= len(self.message):
            return False
        else:
            return True
