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
import warnings
from typing import Any, Callable

from swimai.structures import RecordMap, Slot, Text, RecordConverter, Attr, Record, Item


def before_open(function: 'Callable') -> 'Callable':
    # TODO add unit test for kwargs
    def wrapper(*args, **kwargs):
        if args[0].is_open:
            warnings.warn(f'Cannot execute "{function.__name__}" after the downlink has been opened!')
        else:
            return function(*args, **kwargs)

    return wrapper


# TODO add unit test
def after_open(function: 'Callable') -> 'Callable':
    def wrapper(*args, **kwargs):
        if not args[0].is_open:
            warnings.warn(f'Cannot execute "{function.__name__}" before the downlink has been opened!')
        else:
            return function(*args, **kwargs)

    return wrapper


def convert_to_async(function: 'Any') -> 'Callable':
    async def async_func(*args):
        return function(*args)

    return async_func


class MapRequest:

    def __init__(self, key: Any, value: Any = None) -> None:
        self.key = key
        self.value = value

    def get_key_item(self) -> 'Record':
        key_slot = RecordMap.create()
        key_slot.add(
            Slot.create_slot(Text.create_from('key'), RecordConverter.get_converter().object_to_record(self.key)))

        return key_slot

    def get_value_item(self) -> 'Item':
        value_slot = RecordConverter.get_converter().object_to_record(self.value)
        return value_slot


class UpdateRequest(MapRequest):

    def to_record(self) -> 'Record':
        key_slot = self.get_key_item()
        value_slot = self.get_value_item()

        update_record = RecordMap.create_record_map(Attr.create_attr(Text.create_from('update'), key_slot))
        update_record.add(value_slot)
        return update_record


class RemoveRequest(MapRequest):
    def to_record(self) -> 'Record':
        key_slot = self.get_key_item()

        remove_record = RecordMap.create_record_map(Attr.create_attr(Text.create_from('remove'), key_slot))
        return remove_record
