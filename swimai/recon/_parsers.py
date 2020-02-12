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

from ._utils import _ReconUtils, _InputMessage, _OutputMessage
from swimai.structures import Text, Bool, Attr, Value, Slot, Num, RecordMap
from swimai.structures._structs import _Item, _Record, _ValueBuilder


class _ReconParser:

    @staticmethod
    async def _create_ident(value: str) -> 'Value':
        if value == 'true':
            return Bool.create_from(True)
        elif value == 'false':
            return Bool.create_from(False)

        return Text.create_from(value)

    @staticmethod
    async def _create_attr(key: Any, value: Any = Value.extant()) -> 'Attr':
        return Attr.create_attr(key, value)

    @staticmethod
    async def _create_record_builder() -> 'RecordMap':
        return _Record.create()

    @staticmethod
    async def _create_value_builder() -> '_ValueBuilder':
        return _ValueBuilder()

    @staticmethod
    async def _create_slot(key: Any, value: Any = None) -> 'Slot':
        return Slot.create_slot(key, value)

    @staticmethod
    async def _create_number(value: Union[float, int]) -> 'Num':
        return Num.create_from(value)

    async def _parse_block_string(self, recon_string: str) -> 'Value':
        message = await _InputMessage._create(recon_string)
        return await self._parse_block_expression(message)

    async def _parse_block_expression(self, message: '_InputMessage') -> 'Value':
        return await self._parse_attr_expression(message)

    async def _parse_attr_expression(self, message: '_InputMessage', builder: Union[RecordMap, _ValueBuilder] = None,
                                     field_output: 'Value' = None, value_output: 'Value' = None) -> 'Value':
        return await _AttrExpressionParser._parse(message=message, parser=self, builder=builder,
                                                  field_output=field_output, value_output=value_output)

    async def _parse_attr(self, message: '_InputMessage', key_output: 'Value' = None,
                          value_output: 'Value' = None) -> 'Attr':

        return await _AttrParser._parse(message=message, parser=self, key_output=key_output, value_output=value_output)

    async def _parse_string(self, message: '_InputMessage', output: '_OutputMessage' = None) -> 'Text':
        return await _StringParser._parse(message=message, parser=self, output=output)

    async def _parse_number(self, message: '_InputMessage', value_output: int = None, sign_output: int = 1) -> 'Num':
        return await _NumberParser._parse(message=message, parser=self, value_output=value_output,
                                          sign_output=sign_output)

    async def _parse_literal(self, message: '_InputMessage',
                             builder: Union[RecordMap, _ValueBuilder] = None) -> 'Value':
        return await _LiteralParser._parse(message=message, parser=self, builder=builder)

    async def _parse_record(self, message: '_InputMessage', builder: Union[RecordMap, _ValueBuilder] = None,
                            key_output: 'Value' = None, value_output: 'Value' = None) -> 'Value':
        return await _RecordParser._parse(message=message, parser=self, builder=builder, key_output=key_output,
                                          value_output=value_output)

    async def _parse_ident(self, message: '_InputMessage', output: '_OutputMessage' = None) -> 'Value':
        return await _IdentParser._parse(message=message, parser=self, output=output)


class _AbstractParser(ABC):
    @staticmethod
    @abstractmethod
    async def _parse() -> '_Item':
        """
        Parse a message into its Item object representation.

        :return:                - Item object.
        """
        raise NotImplementedError


class _RecordParser(_AbstractParser):

    @staticmethod
    async def _parse(message: '_InputMessage' = _InputMessage(), parser: '_ReconParser' = None,
                     builder: Union[RecordMap, _ValueBuilder] = None, key_output: 'Value' = None,
                     value_output: 'Value' = None) -> 'Value':

        if builder is None:
            builder = await parser._create_record_builder()

        char = message._head

        if char == '{' or char == '[':
            message._step()

        await message._skip_spaces(message)

        if key_output is None:
            key_output = await parser._parse_block_expression(message)

        await message._skip_spaces(message)

        if message._is_cont:
            if message._head == ':':
                message._step()

                if value_output is None:
                    value_output = await parser._parse_block_expression(message)

            builder.add(await parser._create_slot(key_output, value_output))
            key_output = None

            char = message._head

            if char == ',' or char == ';':
                message._step()
                await _RecordParser._parse(message, parser, builder)

            elif char == '}' or char == ']':
                message._step()

        if key_output:
            builder.add(await parser._create_slot(key_output, value_output))

        return builder._bind()


class _AttrExpressionParser(_AbstractParser):

    @staticmethod
    async def _parse(message: '_InputMessage' = _InputMessage(), parser: '_ReconParser' = None,
                     builder: Union[RecordMap, _ValueBuilder] = None, field_output: 'Value' = None,
                     value_output: 'Value' = None) -> 'Value':

        await message._skip_spaces(message)

        char = message._head

        if char == '@':

            if field_output is None:
                field_output = await parser._parse_attr(message)

            if builder is None:
                builder = await parser._create_record_builder()

            builder.add(field_output)
            await _AttrExpressionParser._parse(message, parser, builder)
            return builder._bind()

        elif await _ReconUtils._is_ident_start_char(char) or char == '"' or await _ReconUtils._is_digit(
                char) or char == '-':

            if value_output is None:
                value_output = await parser._parse_literal(message)

            if builder is None:
                builder = await parser._create_value_builder()

            builder.add(value_output)
            await _AttrExpressionParser._parse(message, parser, builder)
            return builder._bind()

        elif char == '{' or char == '[':
            return await parser._parse_literal(message, builder)


class _AttrParser(_AbstractParser):

    @staticmethod
    async def _parse(message: '_InputMessage' = _InputMessage(), parser: '_ReconParser' = None,
                     key_output: 'Value' = None, value_output: 'Value' = None) -> 'Attr':

        await message._skip_spaces(message)

        char = message._head

        if char == '@':
            message._step()

            if key_output is None:
                key_output = await parser._parse_ident(message)

            if message._head == '(' and message._is_cont:
                message._step()
            else:
                return await parser._create_attr(key_output)

            if value_output is None:
                value_output = await parser._parse_record(message)
                message._step()
                return await parser._create_attr(key_output, value_output)

        if key_output is None or value_output is None:
            raise TypeError(f'Attribute starting at position {message.index} is invalid!\nMessage: {message._value}')
        else:
            return await parser._create_attr(key_output, value_output)


class _IdentParser(_AbstractParser):

    @staticmethod
    async def _parse(message: '_InputMessage' = _InputMessage(), parser: '_ReconParser' = None,
                     output: '_OutputMessage' = None) -> 'Value':

        await message._skip_spaces(message)

        char = message._head

        if await _ReconUtils._is_ident_start_char(char):
            if output is None:
                output = await _OutputMessage._create()

            await output._append(char)
            char = message._step()

            while await _ReconUtils._is_ident_char(char):
                await output._append(char)
                char = message._step()

        if output is not None:
            return await parser._create_ident(output._value)
        else:
            raise TypeError(f'Identifier starting at position {message.index} is invalid!\nMessage: {message._value}')


class _StringParser(_AbstractParser):

    @staticmethod
    async def _parse(message: '_InputMessage' = None, parser: '_ReconParser' = None,
                     output: '_OutputMessage' = None) -> 'Text':

        await message._skip_spaces(message)

        char = message._head

        if char == '"':

            if output is None:
                output = await _OutputMessage._create()

            char = message._step()

            while char != '"' and message._is_cont:
                await output._append(char)
                char = message._step()

            message._step()

        if output is None:
            output = _OutputMessage()

        return Text.create_from(output._value)


class _NumberParser(_AbstractParser):

    @staticmethod
    async def _parse(message: '_InputMessage' = None, parser: '_ReconParser' = None, value_output: int = None,
                     sign_output: int = 1) -> Num:

        await message._skip_spaces(message)

        char = message._head

        if char == '-':
            sign_output = -1
            char = message._step()

        while char == '0':
            char = message._step()

        if '1' <= char <= '9':
            value_output = sign_output * int(char)
            char = message._step()

            while message._is_cont and await _ReconUtils._is_digit(char):
                value_output = 10 * value_output + sign_output * int(char)
                char = message._step()

        if message._is_cont and char == '.':
            return await _DecimalParser._parse(message, parser, value_output, sign_output)
        else:
            if value_output is None:
                value_output = 0

            return await parser._create_number(value_output)


class _DecimalParser(_AbstractParser):

    @staticmethod
    async def _parse(message: '_InputMessage' = _InputMessage(), parser: '_ReconParser' = None,
                     value_output: int = None,
                     sign_output: int = 0) -> 'Num':

        await message._skip_spaces(message)

        builder = await _OutputMessage._create('')

        if sign_output < 0 and value_output is None:
            await builder._append('-0')
        else:
            if value_output is None:
                value_output = 0

            await builder._append(value_output)

        char = message._head

        if char == '.':
            await builder._append('.')
            message._step()

            if message._is_cont:
                char = message._head

                if await _ReconUtils._is_digit(char):
                    await builder._append(char)
                    char = message._step()

                    while message._is_cont and await _ReconUtils._is_digit(char):
                        await builder._append(char)
                        char = message._step()

        return await parser._create_number(float(builder._message))


class _LiteralParser(_AbstractParser):

    @staticmethod
    async def _parse(message: '_InputMessage' = _InputMessage(), parser: '_ReconParser' = None,
                     builder: Union[RecordMap, _ValueBuilder] = None, value_output: int = None) -> Value:

        await message._skip_spaces(message)

        char = message._head

        if char == '{' or char == '[':

            if builder is None:
                builder = await parser._create_record_builder()

            await parser._parse_record(message, builder)

        elif await _ReconUtils._is_ident_start_char(char):
            value_output = await parser._parse_ident(message)
        elif char == '"':
            value_output = await parser._parse_string(message)
        elif char == '-' or await _ReconUtils._is_digit(char):
            value_output = await parser._parse_number(message)

        if builder is None:
            builder = await parser._create_value_builder()

        if value_output is not None:
            builder.add(value_output)

        return builder._bind()
