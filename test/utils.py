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
import asyncio
from typing import Any
from unittest.mock import MagicMock

from swimai.client.connections import ConnectionStatus
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


class MockAsyncFunction(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super(MockAsyncFunction, self).__call__(*args, **kwargs)


class MockWebsocketConnect(MagicMock):

    async def __call__(self, *args, **kwargs):
        return super(MockWebsocketConnect, self).__call__(*args, **kwargs)

    @property
    def return_value(self):
        return MockWebsocket.get_mock_websocket()

    @staticmethod
    def set_raise_exception(state):
        MockWebsocket.get_mock_websocket().raise_exception = state


class MockDownlink:
    instance = None

    def __init__(self):
        self.all_messages_sent = asyncio.Event()
        self.call_counts_left = 0

    async def receive_message(self):

        self.call_counts_left = self.call_counts_left - 1

        if self.call_counts_left == 0:
            self.all_messages_sent.set()

    @staticmethod
    def get_mock_downlink():
        if MockDownlink.instance is None:
            MockDownlink.instance = MockDownlink()

        return MockDownlink.instance

    @staticmethod
    def clear():
        MockDownlink.instance = None


class MockReceiveMessage(MagicMock):

    async def __call__(self, *args, **kwargs):
        await MockDownlink.get_mock_downlink().receive_message()
        return super(MockReceiveMessage, self).__call__(*args, **kwargs)

    @staticmethod
    def set_call_count(call_count):
        MockDownlink.get_mock_downlink().call_counts_left = call_count

    @staticmethod
    def all_messages_has_been_sent():
        return MockDownlink.get_mock_downlink().all_messages_sent


class MockWebsocket:
    instance = None

    def __init__(self):
        self.connection = None
        self.closed = False
        self.sent_messages = list()
        self.messages_to_send = list()
        self.raise_exception = False

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

    async def send(self, message):
        self.sent_messages.append(message)

    async def recv(self):

        if self.raise_exception:
            raise Exception('WebSocket Exception!')

        message = self.messages_to_send.pop()

        if len(self.messages_to_send) == 0:
            self.connection.status = ConnectionStatus.CLOSED

        return message


class MockConnection:
    instance = None

    def __init__(self):
        self.messages_sent = list()

    @staticmethod
    def get_mock_connection():
        if MockConnection.instance is None:
            MockConnection.instance = MockConnection()

        return MockConnection.instance

    @staticmethod
    def clear():
        MockConnection.instance = None

    async def wait_for_messages(self):
        pass

    async def send_message(self, message):
        self.messages_sent.append(message)


async def mock_did_set_callback(old, new):
    str(old)
    str(new)
    pass


async def mock_on_event_callback(event):
    str(event)
    pass


async def mock_did_update_callback(key, old, new):
    str(key)
    str(old)
    str(new)
    pass


async def mock_did_remove_callback(key, old):
    str(key)
    str(old)
    pass


def mock_exception_callback():
    print('Mock exception callback')


class MockRaiseException(MagicMock):

    def __call__(self, *args, **kwargs):
        return super(MockRaiseException, self).__call__(*args, **kwargs)

    @property
    def return_value(self):
        return self.mock_raise_exception()

    def mock_raise_exception(self):
        raise Exception('Mock exception')


class MockScheduleTask:
    instance = None

    def __init__(self):
        self.message = None
        self.call_count = 0

    @staticmethod
    async def async_execute(message):
        MockScheduleTask.instance.message = message
        MockScheduleTask.instance.call_count = MockScheduleTask.instance.call_count + 1

    @staticmethod
    def sync_execute(message):
        MockScheduleTask.instance.message = message
        MockScheduleTask.instance.call_count = MockScheduleTask.instance.call_count + 1

    @staticmethod
    async def async_exception_execute(message):
        MockScheduleTask.instance.message = message
        MockScheduleTask.instance.call_count = MockScheduleTask.instance.call_count + 1
        raise Exception('Mock async execute exception')

    @staticmethod
    def sync_exception_execute(message):
        MockScheduleTask.instance.message = message
        MockScheduleTask.instance.call_count = MockScheduleTask.instance.call_count + 1
        raise Exception('Mock sync execute exception')

    @staticmethod
    async def async_infinite_cancel_execute():
        while True:
            await asyncio.sleep(1)

    @staticmethod
    def get_mock_schedule_task():
        if MockScheduleTask.instance is None:
            MockScheduleTask.instance = MockScheduleTask()

        return MockScheduleTask.instance

    @staticmethod
    def clear():
        MockScheduleTask.instance = None


class MockClass:

    def __init__(self):
        pass


class MockPerson:

    def __init__(self, name=None, age=None, friend=None):
        self.name = name
        self.age = age
        self.friend = friend


class MockPet:
    def __init__(self, name=None, age=None):
        self.name = name
        self.age = age


class MockCar:

    def __init__(self, make=None, model=None, year=None):
        self.make = make
        self.model = model
        self.year = year
