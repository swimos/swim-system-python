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

import asyncio
import inspect

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from ..utils import URI
from swimai.structures import Absent, Value, Attr, Slot, RecordMap, Bool, Num, Text
from swimai.warp import SyncRequest, CommandMessage, Envelope

# Imports for type annotations
if TYPE_CHECKING:
    from ..swim_client import SwimClient
    from ..connections import DownlinkManager


class ValueDownlinkModel:

    def __init__(self, client: 'SwimClient') -> None:
        self.client = client
        self.host_uri = None
        self.node_uri = None
        self.lane_uri = None
        self.form = None
        self.connection = None
        self.task = None
        self.downlink_manager = None
        self.value = Value.absent()

        self.linked = asyncio.Event()
        self.synced = asyncio.Event()

    def open(self) -> 'ValueDownlinkModel':
        self.task = self.client.schedule_task(self.connection.wait_for_messages)
        return self

    def close(self) -> 'ValueDownlinkModel':
        self.client.schedule_task(self.__close)
        return self

    async def establish_downlink(self) -> None:
        """
        Send a `sync` request in order to initiate a connection to a lane from the remote agent.
        """
        sync_request = SyncRequest(self.node_uri, self.lane_uri)
        await self.connection.send_message(await sync_request.to_recon())

    async def receive_message(self, message: 'Envelope') -> None:
        """
        Handle a message from the remote agent.

        :param message:         - Message received from the remote agent.
        """
        if message.tag == 'linked':
            self.linked.set()
        elif message.tag == 'synced':
            self.synced.set()
        elif message.tag == 'event':
            await self.__set_value(message)

    async def send_message(self, message: 'Envelope') -> None:
        """
        Send a message to the remote agent of the downlink.

        :param message:         - Message to send to the remote agent.
        """
        await self.linked.wait()
        await self.connection.send_message(await message.to_recon())

    async def get_value(self) -> Any:
        """
        Get the value of the downlink after it has been synced.

        :return:                - The current value of the downlink.
        """
        await self.synced.wait()
        return self.value

    async def __set_value(self, message: 'Envelope') -> None:
        """
        Set the value of the the downlink and trigger the `did_set` callback of the downlink subscribers.

        :param message:        - The message from the remote agent.
        :return:
        """
        old_value = self.value

        if message.body == Absent.get_absent():
            self.value = None
        elif isinstance(message.body, (Text, Num, Bool)):
            self.value = message.body
        else:
            self.value = await self.record_to_object(message.body)

        await self.downlink_manager.subscribers_did_set(self.value, old_value)

    async def record_to_object(self, body):
        new_object = None

        for item in body.get_items():
            if isinstance(item, Attr):
                class_name = item.key.value
                class_object = self.downlink_manager.registered_classes.get(class_name)

                if class_object is not None:
                    new_object = class_object()
                elif not self.downlink_manager.strict:
                    new_object = type(str(class_name), (object,), {})
                else:
                    raise Exception(f'Missing class for {class_name}')

            if isinstance(item, Slot):

                if isinstance(item.value, RecordMap):
                    setattr(new_object, item.key.value, await self.record_to_object(item.value))
                else:
                    setattr(new_object, item.key.value, item.value.value)

        return new_object

    async def __close(self) -> None:
        self.task.cancel()


class ValueDownlinkView:

    def __init__(self, client: 'SwimClient') -> None:
        self.client = client
        self.host_uri = None
        self.node_uri = None
        self.lane_uri = None
        self.did_set_callback = None
        self.is_open = False
        self.initialised = asyncio.Event()
        self.model = None
        self.connection = None
        self.registered_classes = dict()
        self.strict = True

    @property
    def route(self) -> str:
        return f'{self.node_uri}/{self.lane_uri}'

    def open(self) -> 'ValueDownlinkView':

        if not self.is_open:
            self.is_open = True
            self.client.schedule_task(self.client.add_downlink_view, self)

        return self

    def close(self) -> 'ValueDownlinkView':

        if self.is_open:
            self.is_open = False
            self.client.schedule_task(self.client.remove_downlink_view, self)

        return self

    async def create_downlink_model(self, downlink_manager: 'DownlinkManager') -> 'ValueDownlinkModel':
        model = ValueDownlinkModel(self.client)
        downlink_manager.registered_classes = self.registered_classes
        downlink_manager.strict = self.strict
        model.downlink_manager = downlink_manager
        model.host_uri = self.host_uri
        model.node_uri = self.node_uri
        model.lane_uri = self.lane_uri
        return model

    def set_host_uri(self, host_uri: str) -> 'ValueDownlinkView':
        self.host_uri = URI.normalise_warp_scheme(host_uri)
        return self

    def set_node_uri(self, node_uri: str) -> 'ValueDownlinkView':
        self.node_uri = node_uri
        return self

    def set_lane_uri(self, lane_uri: str) -> 'ValueDownlinkView':
        self.lane_uri = lane_uri
        return self

    def did_set(self, function: Callable) -> 'ValueDownlinkView':

        if inspect.iscoroutinefunction(function) or isinstance(function, Callable):
            self.did_set_callback = function
        else:
            raise TypeError('Callback must be a coroutine or function!')

        return self

    def set_strict(self, status: bool):
        self.strict = status

    def get(self, wait_sync: bool = False) -> Any:
        """
        Return the value of the downlink.

        :param wait_sync:       - If True, wait for the initial `sync` to be completed before returning.
                                  If False, return immediately.
        :return:                - The value of the Downlink.
        """
        if self.is_open:
            if wait_sync:
                task = self.client.schedule_task(self.model.get_value)
                return task.result()
            else:
                return self.model.value
        else:
            raise RuntimeError('Link is not open!')

    def set(self, value: Any) -> None:
        """
        Send a command message to set the value of the lane on the remote agent to the given value.

        :param value:           - New value for the lane of the remote agent.
        """
        if self.is_open:
            message = CommandMessage(self.node_uri, self.lane_uri, value)
            self.client.schedule_task(self.send_message, message)
        else:
            raise RuntimeError('Link is not open!')

    # noinspection PyAsyncCall
    async def execute_did_set(self, current_value: Any, old_value: Any) -> None:
        """
        Execute the custom `did_set` callback of the current downlink view.

        :param current_value:       - The new value of the downlink.
        :param old_value:           - The previous value of the downlink.
        """
        if self.did_set_callback:
            self.client.schedule_task(self.did_set_callback, current_value, old_value)

    async def send_message(self, message: Envelope) -> None:
        """
        Send a message to the remote agent of the downlink.

        :param message:         - Message to send to the remote agent.
        """
        await self.initialised.wait()
        await self.model.send_message(message)

    def register_classes(self, classes_list: list) -> None:
        for custom_class in classes_list:
            self.client.schedule_task(self.__register_class, custom_class)

    def register_class(self, custom_class: Any) -> None:
        self.client.schedule_task(self.__register_class, custom_class)

    def __register_class(self, custom_class: Any) -> None:
        try:
            custom_class()
            self.registered_classes[custom_class.__name__] = custom_class
        except Exception:
            raise Exception(
                f'Class {custom_class.__name__} must have a default constructor or default values for all arguments!')
