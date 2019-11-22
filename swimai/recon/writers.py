#  Copyright 2015-2019 SWIM.AI inc.
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

from .utils import ReconUtils, OutputMessage
from swimai.structures import Attr, Slot, Value, Record, Text, Absent, Num, Extant, Bool, Item


class ReconWriter:

    @staticmethod
    async def write_text(value: str) -> 'OutputMessage':
        if await ReconUtils.is_ident(value):
            return await IdentWriter.write(value=value)
        else:
            return await StringWriter.write(value=value)

    @staticmethod
    async def write_number(value: Union[int, float]) -> 'OutputMessage':
        return await NumberWriter.write(value=value)

    @staticmethod
    async def write_bool(value: bool) -> 'OutputMessage':
        return await BoolWriter.write(value=value)

    @staticmethod
    async def write_absent() -> 'OutputMessage':
        return await OutputMessage.create()

    async def write_item(self, item: 'Item') -> 'str':

        if isinstance(item, Attr):
            output = await self.write_attr(item.key, item.value)
            return output.message
        elif isinstance(item, Slot):
            output = await self.write_slot(item.key, item.value)
            return output.message
        elif isinstance(item, Value):
            output = await self.write_value(item)
            return output.message

        raise TypeError(f'No Recon serialization for {type(item).__name__}!')

    async def write_attr(self, key: 'Value', value: 'Value') -> 'OutputMessage':
        return await AttrWriter.write(key=key, writer=self, value=value)

    async def write_slot(self, key: 'Value', value: 'Value') -> 'OutputMessage':
        return await SlotWriter.write(key=key, writer=self, value=value)

    async def write_value(self, value: Value) -> 'OutputMessage':
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

    async def write_record(self, record: 'Record') -> Optional['OutputMessage']:
        if record.size > 0:
            message = await BlockWriter.write(items=record.get_items(), writer=self, first=True)
            return message


class Writer(ABC):
    @staticmethod
    @abstractmethod
    async def write() -> 'OutputMessage':
        """
        Write an Item object into its string representation.

        :return:                - OutputMessage containing the string representation of the Item object.
        """
        raise NotImplementedError


class BlockWriter(Writer):

    @staticmethod
    async def write(items: List[Item] = None, writer: 'ReconWriter' = None, first: 'bool' = False,
                    in_braces: bool = False) -> 'OutputMessage':
        output = await OutputMessage.create()

        for item in items:

            if isinstance(item, Attr):
                item_text = await writer.write_item(item)
                await output.append(item_text)
            elif isinstance(item, Value) and not isinstance(item, Record):
                item_text = await writer.write_item(item)
                await output.append(item_text)
            else:
                if not first:
                    await output.append(',')
                elif isinstance(item, Slot):
                    if output.size > 0 and output.last_char != '(':
                        await output.append('{')
                        in_braces = True

                item_text = await writer.write_item(item)
                await output.append(item_text)
                first = False

        if in_braces:
            await output.append('}')

        return output


class AttrWriter(Writer):

    @staticmethod
    async def write(key: 'Value' = None, writer: 'ReconWriter' = None, value: 'Value' = None) -> 'OutputMessage':

        output = await OutputMessage.create('@')
        key_text = await writer.write_value(key)

        if key_text:
            await output.append(key_text)

        if value != Extant.get_extant() and value is not None:
            await output.append('(')
            value_text = await writer.write_value(value)
            await output.append(value_text)
            await output.append(')')

        return output


class SlotWriter(Writer):

    @staticmethod
    async def write(key: Value = None, writer: 'ReconWriter' = None, value: 'Value' = None) -> 'OutputMessage':

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
    async def write(value: str = None) -> 'OutputMessage':
        output = await OutputMessage.create('"')

        if value:
            await output.append(value)

        await output.append('"')

        return output


class NumberWriter(Writer):

    @staticmethod
    async def write(value: Union[int, float] = None) -> 'OutputMessage':
        output = await OutputMessage().create()

        if value:
            await output.append(value)

        return output


class BoolWriter(Writer):

    @staticmethod
    async def write(value: bool = None) -> 'OutputMessage':

        if value:
            return await OutputMessage.create('true')
        else:
            return await OutputMessage.create('false')


class IdentWriter(Writer):

    @staticmethod
    async def write(value: str = None) -> 'OutputMessage':
        output = await OutputMessage.create()

        if value:
            await output.append(value)

        return output
