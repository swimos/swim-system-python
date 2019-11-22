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

from typing import Any
from unittest.mock import MagicMock

from swimai.structures import Item


class CustomString:
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        return self.value == other

    def __str__(self):
        return f'CustomString({self.value})'


class CustomItem(Item):
    @property
    def key(self) -> 'Any':
        return 'MockKey'

    @property
    def value(self) -> 'Any':
        return 'MockVale'


class AsyncMock(MagicMock):

    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)

    @property
    def return_value(self):
        return MockWebsocket.get_mock_websocket()


class MockWebsocket:
    instance = None

    def __init__(self):
        self.closed = False

    @staticmethod
    def get_mock_websocket():
        if MockWebsocket.instance is None:
            MockWebsocket.instance = MockWebsocket()

        return MockWebsocket.instance

    @staticmethod
    def clear():
        MockWebsocket.instance = None

    async def close(self):
        self.closed = True
