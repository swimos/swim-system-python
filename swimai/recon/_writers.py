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
from typing import Union, List, Optional

from ._utils import _ReconUtils, _OutputMessage
from swimai.structures import Attr, Slot, Value, Text, Num, Bool
from swimai.structures._structs import _Absent, _Item, _Extant, _Record


class _ReconWriter:

    @staticmethod
    async def _write_text(value: str) -> '_OutputMessage':
        if await _ReconUtils._is_ident(value):
            return await _IdentWriter._write(value=value)
        else:
            return await _StringWriter._write(value=value)

    @staticmethod
    async def _write_number(value: Union[int, float]) -> '_OutputMessage':
        return await _NumberWriter._write(value=value)

    @staticmethod
    async def _write_bool(value: bool) -> '_OutputMessage':
        return await _BoolWriter._write(value=value)

    @staticmethod
    async def _write_absent() -> '_OutputMessage':
        return await _OutputMessage._create()

    async def _write_item(self, item: '_Item') -> 'str':

        if isinstance(item, Attr):
            output = await self._write_attr(item.key, item.value)
            return output._message
        elif isinstance(item, Slot):
            output = await self._write_slot(item.key, item.value)
            return output._message
        elif isinstance(item, Value):
            output = await self._write_value(item)
            return output._message

        raise TypeError(f'No Recon serialization for {type(item).__name__}!')

    async def _write_attr(self, key: 'Value', value: 'Value') -> '_OutputMessage':
        return await _AttrWriter._write(key=key, writer=self, value=value)

    async def _write_slot(self, key: 'Value', value: 'Value') -> '_OutputMessage':
        return await _SlotWriter._write(key=key, writer=self, value=value)

    async def _write_value(self, value: Value) -> '_OutputMessage':
        if isinstance(value, _Record):
            return await self._write_record(value)
        elif isinstance(value, Text):
            return await self._write_text(value.get_string_value())
        elif isinstance(value, Num):
            return await self._write_number(value.get_num_value())
        elif isinstance(value, Bool):
            return await self._write_bool(value.get_bool_value())
        elif isinstance(value, _Absent):
            return await self._write_absent()

    async def _write_record(self, record: '_Record') -> Optional['_OutputMessage']:
        if record.size > 0:
            message = await _BlockWriter._write(items=record.get_items(), writer=self, first=True)
            return message


class _AbstractWriter(ABC):
    @staticmethod
    @abstractmethod
    async def _write() -> '_OutputMessage':
        """
        Write an Item object into its string representation.

        :return:                - OutputMessage containing the string representation of the Item object.
        """
        raise NotImplementedError


class _BlockWriter(_AbstractWriter):

    @staticmethod
    async def _write(items: List[_Item] = None, writer: '_ReconWriter' = None, first: 'bool' = False,
                     in_braces: bool = False) -> '_OutputMessage':
        output = await _OutputMessage._create()

        for item in items:

            if isinstance(item, Attr):
                item_text = await writer._write_item(item)
                await output._append(item_text)
            elif isinstance(item, Value) and not isinstance(item, _Record):
                item_text = await writer._write_item(item)
                await output._append(item_text)
            else:
                if not first:
                    await output._append(',')
                elif isinstance(item, Slot):
                    if output._size > 0 and output._last_char != '(':
                        await output._append('{')
                        in_braces = True

                item_text = await writer._write_item(item)
                await output._append(item_text)
                first = False

        if in_braces:
            await output._append('}')

        return output


class _AttrWriter(_AbstractWriter):

    @staticmethod
    async def _write(key: 'Value' = None, writer: '_ReconWriter' = None, value: 'Value' = None) -> '_OutputMessage':

        output = await _OutputMessage._create('@')
        key_text = await writer._write_value(key)

        if key_text:
            await output._append(key_text)

        if value != _Extant._get_extant() and value is not None:
            await output._append('(')
            value_text = await writer._write_value(value)
            await output._append(value_text)
            await output._append(')')

        return output


class _SlotWriter(_AbstractWriter):

    @staticmethod
    async def _write(key: Value = None, writer: '_ReconWriter' = None, value: 'Value' = None) -> '_OutputMessage':

        output = await _OutputMessage._create()
        key_text = await writer._write_value(key)

        if key_text:
            await output._append(key_text)

        await output._append(':')
        value_text = await writer._write_value(value)

        if value_text:
            await output._append(value_text)

        return output


class _StringWriter(_AbstractWriter):

    @staticmethod
    async def _write(value: str = None) -> '_OutputMessage':
        output = await _OutputMessage._create('"')

        if value:
            await output._append(value)

        await output._append('"')

        return output


class _NumberWriter(_AbstractWriter):

    @staticmethod
    async def _write(value: Union[int, float] = None) -> '_OutputMessage':
        output = await _OutputMessage()._create()

        if value is not None:
            await output._append(value)

        return output


class _BoolWriter(_AbstractWriter):

    @staticmethod
    async def _write(value: bool = None) -> '_OutputMessage':

        if value:
            return await _OutputMessage._create('true')
        else:
            return await _OutputMessage._create('false')


class _IdentWriter(_AbstractWriter):

    @staticmethod
    async def _write(value: str = None) -> '_OutputMessage':
        output = await _OutputMessage._create()

        if value:
            await output._append(value)

        return output
