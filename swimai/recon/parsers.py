#  Copyright 2015-2020 SWIM.AI inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from abc import ABC, abstractmethod
from typing import Union, Any

from .utils import ReconUtils, InputMessage, OutputMessage
from swimai.structures import ValueBuilder, Text, Bool, Attr, Value, Record, Slot, Num, RecordMap, Item


class ReconParser:

    @staticmethod
    async def create_ident(value: str) -> 'Value':
        if value == 'true':
            return Bool.create_from(True)
        elif value == 'false':
            return Bool.create_from(False)

        return Text.create_from(value)

    @staticmethod
    async def create_attr(key: Any, value: Any = Value.extant()) -> 'Attr':
        return Attr.create_attr(key, value)

    @staticmethod
    async def create_record_builder() -> 'RecordMap':
        return Record.create()

    @staticmethod
    async def create_value_builder() -> 'ValueBuilder':
        return ValueBuilder()

    @staticmethod
    async def create_slot(key: Any, value: Any = None) -> 'Slot':
        return Slot.create_slot(key, value)

    @staticmethod
    async def create_number(value: Union[float, int]) -> 'Num':
        return Num.create_from(value)

    async def parse_block_string(self, recon_string: str) -> 'Value':
        message = await InputMessage.create(recon_string)
        return await self.parse_block_expression(message)

    async def parse_block_expression(self, message: 'InputMessage') -> 'Value':
        return await self.parse_attr_expression(message)

    async def parse_attr_expression(self, message: 'InputMessage', builder: Union[RecordMap, ValueBuilder] = None,
                                    field_output: 'Value' = None, value_output: 'Value' = None) -> 'Value':
        return await AttrExpressionParser.parse(message=message, parser=self, builder=builder,
                                                field_output=field_output, value_output=value_output)

    async def parse_attr(self, message: 'InputMessage', key_output: 'Value' = None,
                         value_output: 'Value' = None) -> 'Attr':

        return await AttrParser.parse(message=message, parser=self, key_output=key_output, value_output=value_output)

    async def parse_string(self, message: 'InputMessage', output: 'OutputMessage' = None) -> 'Text':
        return await StringParser.parse(message=message, parser=self, output=output)

    async def parse_number(self, message: 'InputMessage', value_output: int = None, sign_output: int = 1) -> 'Num':
        return await NumberParser.parse(message=message, parser=self, value_output=value_output,
                                        sign_output=sign_output)

    async def parse_literal(self, message: 'InputMessage', builder: Union[RecordMap, ValueBuilder] = None) -> 'Value':
        return await LiteralParser.parse(message=message, parser=self, builder=builder)

    async def parse_record(self, message: 'InputMessage', builder: Union[RecordMap, ValueBuilder] = None,
                           key_output: 'Value' = None, value_output: 'Value' = None) -> 'Value':
        return await RecordParser.parse(message=message, parser=self, builder=builder, key_output=key_output,
                                        value_output=value_output)

    async def parse_ident(self, message: 'InputMessage', output: 'OutputMessage' = None) -> 'Value':
        return await IdentParser.parse(message=message, parser=self, output=output)


class Parser(ABC):
    @staticmethod
    @abstractmethod
    async def parse() -> 'Item':
        """
        Parse a message into its Item object representation.

        :return:                - Item object.
        """
        raise NotImplementedError


class RecordParser(Parser):

    @staticmethod
    async def parse(message: 'InputMessage' = InputMessage(), parser: 'ReconParser' = None,
                    builder: Union[RecordMap, ValueBuilder] = None, key_output: 'Value' = None,
                    value_output: 'Value' = None) -> 'Value':

        if builder is None:
            builder = await parser.create_record_builder()

        char = message.head

        if char == '{' or char == '[':
            message.step()

        await message.skip_spaces(message)

        if key_output is None:
            key_output = await parser.parse_block_expression(message)

        await message.skip_spaces(message)

        if message.is_cont:
            if message.head == ':':
                message.step()

                if value_output is None:
                    value_output = await parser.parse_block_expression(message)

            builder.add(await parser.create_slot(key_output, value_output))
            key_output = None

            char = message.head

            if char == ',' or char == ';':
                message.step()
                await RecordParser.parse(message, parser, builder)

            elif char == '}' or char == ']':
                message.step()

        if key_output:
            builder.add(await parser.create_slot(key_output, value_output))

        return builder.bind()


class AttrExpressionParser(Parser):

    @staticmethod
    async def parse(message: 'InputMessage' = InputMessage(), parser: 'ReconParser' = None,
                    builder: Union[RecordMap, ValueBuilder] = None, field_output: 'Value' = None,
                    value_output: 'Value' = None) -> 'Value':

        await message.skip_spaces(message)

        char = message.head

        if char == '@':

            if field_output is None:
                field_output = await parser.parse_attr(message)

            if builder is None:
                builder = await parser.create_record_builder()

            builder.add(field_output)
            await AttrExpressionParser.parse(message, parser, builder)
            return builder.bind()

        elif await ReconUtils.is_ident_start_char(char) or char == '"' or await ReconUtils.is_digit(
                char) or char == '-':

            if value_output is None:
                value_output = await parser.parse_literal(message)

            if builder is None:
                builder = await parser.create_value_builder()

            builder.add(value_output)
            await AttrExpressionParser.parse(message, parser, builder)
            return builder.bind()

        elif char == '{' or char == '[':
            return await parser.parse_literal(message, builder)


class AttrParser(Parser):

    @staticmethod
    async def parse(message: 'InputMessage' = InputMessage(), parser: 'ReconParser' = None, key_output: 'Value' = None,
                    value_output: 'Value' = None) -> 'Attr':

        await message.skip_spaces(message)

        char = message.head

        if char == '@':
            message.step()

            if key_output is None:
                key_output = await parser.parse_ident(message)

            if message.head == '(' and message.is_cont:
                message.step()
            else:
                return await parser.create_attr(key_output)

            if value_output is None:
                value_output = await parser.parse_record(message)
                message.step()
                return await parser.create_attr(key_output, value_output)

        if key_output is None or value_output is None:
            raise TypeError(f'Attribute starting at position {message.index} is invalid!\nMessage: {message.value}')
        else:
            return await parser.create_attr(key_output, value_output)


class IdentParser(Parser):

    @staticmethod
    async def parse(message: 'InputMessage' = InputMessage(), parser: 'ReconParser' = None,
                    output: 'OutputMessage' = None) -> 'Value':

        await message.skip_spaces(message)

        char = message.head

        if await ReconUtils.is_ident_start_char(char):
            if output is None:
                output = await OutputMessage.create()

            await output.append(char)
            char = message.step()

            while await ReconUtils.is_ident_char(char):
                await output.append(char)
                char = message.step()

        if output is not None:
            return await parser.create_ident(output.value)
        else:
            raise TypeError(f'Identifier starting at position {message.index} is invalid!\nMessage: {message.value}')


class StringParser(Parser):

    @staticmethod
    async def parse(message: 'InputMessage' = None, parser: 'ReconParser' = None,
                    output: 'OutputMessage' = None) -> 'Text':

        await message.skip_spaces(message)

        char = message.head

        if char == '"':

            if output is None:
                output = await OutputMessage.create()

            char = message.step()

            while char != '"' and message.is_cont:
                await output.append(char)
                char = message.step()

            message.step()

        if output is None:
            output = OutputMessage()

        return Text.create_from(output.value)


class NumberParser(Parser):

    @staticmethod
    async def parse(message: 'InputMessage' = None, parser: 'ReconParser' = None, value_output: int = None,
                    sign_output: int = 1) -> Num:

        await message.skip_spaces(message)

        char = message.head

        if char == '-':
            sign_output = -1
            char = message.step()

        while char == '0':
            char = message.step()

        if '1' <= char <= '9':
            value_output = sign_output * int(char)
            char = message.step()

            while message.is_cont and await ReconUtils.is_digit(char):
                value_output = 10 * value_output + sign_output * int(char)
                char = message.step()

        if message.is_cont and char == '.':
            return await DecimalParser.parse(message, parser, value_output, sign_output)
        else:
            if value_output is None:
                value_output = 0

            return await parser.create_number(value_output)


class DecimalParser(Parser):

    @staticmethod
    async def parse(message: 'InputMessage' = InputMessage(), parser: 'ReconParser' = None, value_output: int = None,
                    sign_output: int = 0) -> 'Num':

        await message.skip_spaces(message)

        builder = await OutputMessage.create('')

        if sign_output < 0 and value_output is None:
            await builder.append('-0')
        else:
            if value_output is None:
                value_output = 0

            await builder.append(value_output)

        char = message.head

        if char == '.':
            await builder.append('.')
            message.step()

            if message.is_cont:
                char = message.head

                if await ReconUtils.is_digit(char):
                    await builder.append(char)
                    char = message.step()

                    while message.is_cont and await ReconUtils.is_digit(char):
                        await builder.append(char)
                        char = message.step()

        return await parser.create_number(float(builder.message))


class LiteralParser(Parser):

    @staticmethod
    async def parse(message: 'InputMessage' = InputMessage(), parser: 'ReconParser' = None,
                    builder: Union[RecordMap, ValueBuilder] = None, value_output: int = None) -> Value:

        await message.skip_spaces(message)

        char = message.head

        if char == '{' or char == '[':

            if builder is None:
                builder = await parser.create_record_builder()

            await parser.parse_record(message, builder)

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
