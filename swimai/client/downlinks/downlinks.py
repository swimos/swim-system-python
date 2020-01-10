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
import inspect

from collections.abc import Callable
from abc import abstractmethod
from typing import TYPE_CHECKING, Any

from ..utils import URI
from swimai.structures import Absent, Value, Bool, Num, Text, RecordConverter
from swimai.warp import SyncRequest, CommandMessage, Envelope, LinkRequest
from .downlink_utils import before_open

# Imports for type annotations
if TYPE_CHECKING:
    from ..swim_client import SwimClient
    from ..connections import DownlinkManager


class DownlinkModel:

    def __init__(self, client: 'SwimClient') -> None:
        self.client = client
        self.host_uri = None
        self.node_uri = None
        self.lane_uri = None
        self.task = None
        self.connection = None
        self.linked = asyncio.Event()

        self.downlink_manager = None

    def open(self) -> 'DownlinkModel':
        self.task = self.client.schedule_task(self.connection.wait_for_messages)
        return self

    def close(self) -> 'DownlinkModel':
        self.client.schedule_task(self.__close)
        return self

    async def __close(self) -> None:
        self.task.cancel()

    @abstractmethod
    async def establish_downlink(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def receive_message(self, message: 'Envelope') -> None:
        raise NotImplementedError


class DownlinkView:

    def __init__(self, client: 'SwimClient') -> None:
        self.client = client
        self.host_uri = None
        self.node_uri = None
        self.lane_uri = None
        self.is_open = False
        self.connection = None
        self.model = None
        self.downlink_manager = None

        self.__registered_classes = dict()
        self.__deregister_classes = set()
        self.__strict = False

    @property
    def route(self) -> str:
        return f'{self.node_uri}/{self.lane_uri}'

    @before_open
    def set_host_uri(self, host_uri: str) -> 'DownlinkView':
        self.host_uri = URI.normalise_warp_scheme(host_uri)
        return self

    @before_open
    def set_node_uri(self, node_uri: str) -> 'DownlinkView':
        self.node_uri = node_uri
        return self

    @before_open
    def set_lane_uri(self, lane_uri: str) -> 'DownlinkView':
        self.lane_uri = lane_uri
        return self

    def open(self) -> 'DownlinkView':
        if not self.is_open:
            self.is_open = True
            self.client.schedule_task(self.client.add_downlink_view, self)

        return self

    def close(self) -> 'DownlinkView':

        if self.is_open:
            self.is_open = False
            self.client.schedule_task(self.client.remove_downlink_view, self)

        return self

    @property
    async def registered_classes(self):
        if self.downlink_manager is None:
            return self.__registered_classes
        else:
            return self.downlink_manager.registered_classes

    @property
    def strict(self):
        if self.downlink_manager is None:
            return self.__strict
        else:
            return self.downlink_manager.strict

    @strict.setter
    def strict(self, strict):
        if self.downlink_manager is not None:
            self.downlink_manager.strict = self.__strict
        else:
            self.__strict = strict

    def register_classes(self, classes_list: list) -> None:
        for custom_class in classes_list:
            self.client.schedule_task(self.__register_class, custom_class)

    def register_class(self, custom_class: Any) -> None:
        self.client.schedule_task(self.__register_class, custom_class)

    def deregister_all_classes(self):
        if self.downlink_manager is not None:
            self.__deregister_classes.update(set(self.downlink_manager.registered_classes.keys()))
            self.downlink_manager.registered_classes.clear()
        else:
            self.__registered_classes.clear()

    def deregister_classes(self, classes_list: list) -> None:
        for custom_class in classes_list:
            self.deregister_class(custom_class)

    def deregister_class(self, custom_class: Any) -> None:
        if self.downlink_manager is not None:
            self.downlink_manager.registered_classes.pop(custom_class.__name__, None)
        else:
            self.__registered_classes.pop(custom_class.__name__, None)
            self.__deregister_classes.add(custom_class.__name__)

    def __register_class(self, custom_class: Any) -> None:
        try:
            custom_class()

            if self.downlink_manager is not None:
                self.downlink_manager.registered_classes[custom_class.__name__] = custom_class
            else:
                self.__registered_classes[custom_class.__name__] = custom_class
                self.__deregister_classes.discard(custom_class.__name__)

        except Exception:
            raise Exception(
                f'Class {custom_class.__name__} must have a default constructor or default values for all arguments!')

    @abstractmethod
    async def register_manager(self, manager: 'DownlinkManager') -> None:
        raise NotImplementedError

    @abstractmethod
    async def create_downlink_model(self, downlink_manager: 'DownlinkManager') -> 'DownlinkModel':
        raise NotImplementedError


class EventDownlinkModel(DownlinkModel):

    async def establish_downlink(self) -> None:
        link_request = LinkRequest(self.node_uri, self.lane_uri)
        await self.connection.send_message(await link_request.to_recon())

    async def receive_message(self, message: 'Envelope') -> None:
        if message.tag == 'linked':
            self.linked.set()
        elif message.tag == 'event':
            await self.receive_event(message)

    async def receive_event(self, message: Envelope):

        if message.body == Absent.get_absent():
            event = Value.absent()
        elif isinstance(message.body, (Text, Num, Bool)):
            event = message.body
        else:
            converter = RecordConverter.get_converter()
            event = converter.record_to_object(message.body, self.downlink_manager.registered_classes,
                                               self.downlink_manager.strict)

        await self.downlink_manager.subscribers_on_event(event)


class EventDownlinkView(DownlinkView):

    def __init__(self, client: 'SwimClient') -> None:
        super().__init__(client)
        self.on_event_callback = None

    async def register_manager(self, manager: 'DownlinkManager') -> None:
        self.model = manager.downlink_model
        self.downlink_manager = manager

    async def create_downlink_model(self, downlink_manager: 'DownlinkManager') -> 'DownlinkModel':
        model = EventDownlinkModel(self.client)
        downlink_manager.registered_classes = await self.registered_classes
        downlink_manager.strict = self.strict
        model.downlink_manager = downlink_manager
        model.host_uri = self.host_uri
        model.node_uri = self.node_uri
        model.lane_uri = self.lane_uri
        return model

    # noinspection PyAsyncCall
    async def execute_on_event(self, event: Any) -> None:
        if self.on_event_callback:
            self.client.schedule_task(self.on_event_callback, event)

    def on_event(self, function: Callable) -> 'EventDownlinkView':

        if inspect.iscoroutinefunction(function) or isinstance(function, Callable):
            self.on_event_callback = function
        else:
            raise TypeError('Callback must be a coroutine or function!')

        return self


class ValueDownlinkModel(DownlinkModel):

    def __init__(self, client: 'SwimClient') -> None:
        super().__init__(client)
        self.value = Value.absent()
        self.synced = asyncio.Event()

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
            self.value = Value.absent()
        elif isinstance(message.body, (Text, Num, Bool)):
            self.value = message.body
        else:
            converter = RecordConverter.get_converter()
            self.value = converter.record_to_object(message.body, self.downlink_manager.registered_classes,
                                                    self.downlink_manager.strict)

        await self.downlink_manager.subscribers_did_set(self.value, old_value)


class ValueDownlinkView(DownlinkView):

    def __init__(self, client: 'SwimClient') -> None:
        super().__init__(client)
        self.did_set_callback = None
        self.initialised = asyncio.Event()

    async def register_manager(self, manager: 'DownlinkManager') -> None:
        self.model = manager.downlink_model
        manager.registered_classes.update(await self.registered_classes)
        manager.strict = self.strict
        self.downlink_manager = manager

        if manager.is_open:
            await self.execute_did_set(self.model.value, Value.absent())

        self.initialised.set()

    async def create_downlink_model(self, downlink_manager: 'DownlinkManager') -> 'ValueDownlinkModel':
        model = ValueDownlinkModel(self.client)
        downlink_manager.registered_classes = await self.registered_classes
        downlink_manager.strict = self.strict
        model.downlink_manager = downlink_manager
        model.host_uri = self.host_uri
        model.node_uri = self.node_uri
        model.lane_uri = self.lane_uri
        return model

    def did_set(self, function: Callable) -> 'ValueDownlinkView':

        if inspect.iscoroutinefunction(function) or isinstance(function, Callable):
            self.did_set_callback = function
        else:
            raise TypeError('Callback must be a coroutine or function!')

        return self

    @property
    def value(self):
        if self.model is None:
            return Value.absent()
        else:
            return self.model.value

    async def __get_value(self):
        await self.initialised.wait()
        return await self.model.get_value()

    def get(self, wait_sync: bool = False) -> Any:
        """
        Return the value of the downlink.

        :param wait_sync:       - If True, wait for the initial `sync` to be completed before returning.
                                  If False, return immediately.
        :return:                - The value of the Downlink.
        """
        if self.is_open:
            if wait_sync:
                task = self.client.schedule_task(self.__get_value)
                return task.result()
            else:
                return self.value
        else:
            raise RuntimeError('Link is not open!')

    def set(self, value: Any, blocking: bool = False) -> None:
        """
        Send a command message to set the value of the lane on the remote agent to the given value.

        :param blocking:        - If True, block until the value has been sent to the server.
        :param value:           - New value for the lane of the remote agent.
        """
        if self.is_open:
            task = self.client.schedule_task(self.send_message, value)

            if blocking:
                task.result()

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

    async def send_message(self, value: Any) -> None:
        """
        Send a message to the remote agent of the downlink.

        :param value:           - New value for the lane of the remote agent.
        """
        await self.initialised.wait()

        recon = RecordConverter.get_converter().object_to_record(value)
        message = CommandMessage(self.node_uri, self.lane_uri, recon)

        await self.model.send_message(message)
