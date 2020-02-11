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
from asyncio import Future

from collections.abc import Callable
from abc import abstractmethod, ABC
from typing import TYPE_CHECKING, Any
from swimai.recon import Recon
from swimai.structures import Value, RecordConverter
from swimai.warp import SyncRequest, CommandMessage, Envelope, LinkRequest
from ..utils import URI
from .downlink_utils import before_open, UpdateRequest, RemoveRequest, after_open, validate_callback

# Imports for type annotations
if TYPE_CHECKING:
    from ..swim_client import SwimClient
    from ..connections import DownlinkManager


class DownlinkModel(ABC):

    def __init__(self, client: 'SwimClient') -> None:
        self.client = client
        self.host_uri = None
        self.node_uri = None
        self.lane_uri = None
        self.task = None
        self.connection = None
        self.linked = asyncio.Event()
        self.downlink_manager = None

    @abstractmethod
    async def establish_downlink(self) -> None:
        """
        Send a request to the remote agent to establish connection.
        """
        raise NotImplementedError

    @abstractmethod
    async def receive_event(self, message: 'Envelope') -> None:
        """
        Handle an `event` response message from the remote agent.

        :param message:          - Event response message.
        """
        raise NotImplementedError

    @abstractmethod
    async def receive_synced(self) -> None:
        """
        Handle a `synced` response message from the remote agent.
        """
        raise NotImplementedError

    def open(self) -> 'DownlinkModel':
        self.task = self.client.schedule_task(self.connection.wait_for_messages)
        self.task.add_done_callback(self.__close_views)
        return self

    def close(self) -> 'DownlinkModel':
        self.client.schedule_task(self.__close)
        return self

    async def receive_message(self, message: 'Envelope') -> None:
        """
        Handle a response message from the remote agent.

        :param message:         - Response message.
        """
        if message.tag == 'linked':
            await self.receive_linked()
        elif message.tag == 'synced':
            await self.receive_synced()
        elif message.tag == 'event':
            await self.receive_event(message)
        elif message.tag == 'unlinked':
            await self.receive_unlinked(message)

    async def receive_linked(self) -> None:
        """
        Handle a `linked` response message from the remote agent.
        """
        self.linked.set()

    async def receive_unlinked(self, message: 'Envelope') -> None:
        """
        Handle an `unlinked` response message from the remote agent.

        :param message          - Response message.
        """
        if message.body.tag == 'laneNotFound':
            raise Exception(f'Lane "{self.lane_uri}" was not found on the remote agent!')

    async def __close(self) -> None:
        self.task.cancel()

    # noinspection PyUnusedLocal
    def __close_views(self, future: Future) -> None:
        if self.downlink_manager is not None:
            self.downlink_manager.close_views()


class DownlinkView(ABC):

    def __init__(self, client: 'SwimClient') -> None:
        self.client = client
        self.host_uri = None
        self.node_uri = None
        self.lane_uri = None
        self.connection = None
        self.model = None
        self.downlink_manager = None
        self.is_open = False

        self.__registered_classes = dict()
        self.__deregistered_classes = set()
        self.__clear_classes = False
        self.__strict = False

    @property
    def route(self) -> str:
        return f'{self.node_uri}/{self.lane_uri}'

    @property
    def strict(self) -> bool:
        """
        The strict status is used when custom objects are received by the downlink. If the downlink is strict,
        a class of the same name, as the object received, must have been registered with the downlink. If the downlink
        is not strict, a custom object will be created dynamically.

        :return:                    - Whether or not the downlink is strict.
        """
        if self.downlink_manager is None:
            return self.__strict
        else:
            return self.downlink_manager.strict

    @strict.setter
    def strict(self, strict: bool) -> None:
        if self.downlink_manager is None:
            self.__strict = strict
        else:
            self.downlink_manager.strict = strict

    @property
    def registered_classes(self) -> dict:
        if self.downlink_manager is None:
            return self.__registered_classes
        else:
            return self.downlink_manager.registered_classes

    @abstractmethod
    async def register_manager(self, manager: 'DownlinkManager') -> None:
        """
        Register the current downlink view with a downlink manager.

        :param manager:             - Downlink manager for the current downlink view.
        """
        raise NotImplementedError

    @abstractmethod
    async def create_downlink_model(self, downlink_manager: 'DownlinkManager') -> 'DownlinkModel':
        """
        Create a downlink model for the current downlink view.

        :param downlink_manager:    - Downlink manager of the current downlink view.
        :return:                    - Downlink model for the current downlink view.
        """
        raise NotImplementedError

    def open(self) -> 'DownlinkView':
        if not self.is_open:
            task = self.client.schedule_task(self.client.add_downlink_view, self)
            if task is not None:
                self.is_open = True

        return self

    def close(self) -> 'DownlinkView':
        if self.is_open:
            self.client.schedule_task(self.client.remove_downlink_view, self)
            self.is_open = False

        return self

    async def initalise_model(self, manager: 'DownlinkManager', model: 'DownlinkModel') -> None:
        """
        Initialise the given downlink model and manager with the values of the current downlink view.

        :param manager:             - Downlink manager for the current downlink view.
        :param model:               - Downlink model for the current downlink view.
        """
        manager.registered_classes = self.registered_classes
        manager.strict = self.strict
        model.downlink_manager = manager
        model.host_uri = self.host_uri
        model.node_uri = self.node_uri
        model.lane_uri = self.lane_uri

    async def assign_manager(self, manager: 'DownlinkManager') -> None:
        """
        Assign a downlink manager to the current downlink view and update the manager with the values
        of the downlink view.

        :param manager:             - Downlink manager to assign to the current downlink view.
        """
        self.model = manager.downlink_model
        manager.registered_classes.update(self.registered_classes)

        for klass in self.__deregistered_classes:
            manager.registered_classes.pop(klass)

        if self.__clear_classes:
            manager.registered_classes.clear()

        manager.strict = self.strict
        self.downlink_manager = manager

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

    def register_class(self, custom_class: Any) -> None:
        """
        Register a class with the downlink view. The registered classes are used for constructing objects when
        events with custom objects are received by the downlink.

        :param custom_class:        - Class to register.
        """
        self.__register_class(custom_class)

    def register_classes(self, classes_list: list) -> None:
        for custom_class in classes_list:
            self.__register_class(custom_class)

    def deregister_class(self, custom_class: Any) -> None:
        """
        Deregister a class from the downlink view and the downlink manager associated with it.

        :param custom_class:        - Class to deregister.
        """
        if self.downlink_manager is None:
            self.__registered_classes.pop(custom_class.__name__, None)
            self.__deregistered_classes.add(custom_class.__name__)
        else:
            self.downlink_manager.registered_classes.pop(custom_class.__name__, None)

    def deregister_classes(self, classes_list: list) -> None:
        for custom_class in classes_list:
            self.deregister_class(custom_class)

    def deregister_all_classes(self) -> None:
        """
        Deregister all classes from the downlink view and the downlink manager associated with it.
        """
        if self.downlink_manager is not None:
            self.__deregistered_classes.update(set(self.downlink_manager.registered_classes.keys()))
            self.downlink_manager.registered_classes.clear()
        else:
            self.__clear_classes = True
            self.__registered_classes.clear()

    def __register_class(self, custom_class: Any) -> None:
        try:
            custom_class()

            if self.downlink_manager is not None:
                self.downlink_manager.registered_classes[custom_class.__name__] = custom_class
            else:
                self.__registered_classes[custom_class.__name__] = custom_class
                self.__deregistered_classes.discard(custom_class.__name__)
        except Exception:
            raise Exception(
                f'Class "{custom_class.__name__}" must have a default constructor or default values for all arguments!')


class EventDownlinkModel(DownlinkModel):

    async def establish_downlink(self) -> None:
        link_request = LinkRequest(self.node_uri, self.lane_uri)
        await self.connection.send_message(await link_request.to_recon())

    async def receive_event(self, message: Envelope) -> None:
        converter = RecordConverter.get_converter()
        event = converter.record_to_object(message.body, self.downlink_manager.registered_classes,
                                           self.downlink_manager.strict)

        await self.downlink_manager.subscribers_on_event(event)

    async def receive_synced(self) -> None:
        raise TypeError('Event downlink does not support synced responses!')


class EventDownlinkView(DownlinkView):

    def __init__(self, client: 'SwimClient') -> None:
        super().__init__(client)
        self.on_event_callback = None

    async def register_manager(self, manager: 'DownlinkManager') -> None:
        await self.assign_manager(manager)

    async def create_downlink_model(self, downlink_manager: 'DownlinkManager') -> 'DownlinkModel':
        model = EventDownlinkModel(self.client)
        await self.initalise_model(downlink_manager, model)
        return model

    def on_event(self, function: Callable) -> 'EventDownlinkView':
        """
        Set the `on_event` callback of the current downlink view to a given function.

        :param function:   - Function to be called when an event is received by the downlink.
        :return:           - The current downlink view.
        """
        self.on_event_callback = validate_callback(function)
        return self

    # noinspection PyAsyncCall
    async def execute_on_event(self, event: Any) -> None:
        """
        Execute the custom `on_event` callback of the current downlink view.

        :param event:       - The event received by the downlink.
        """
        if self.on_event_callback:
            self.client.schedule_task(self.on_event_callback, event)


class ValueDownlinkModel(DownlinkModel):

    def __init__(self, client: 'SwimClient') -> None:
        super().__init__(client)
        self.value = Value.absent()
        self.synced = asyncio.Event()

    async def establish_downlink(self) -> None:
        sync_request = SyncRequest(self.node_uri, self.lane_uri)
        await self.connection.send_message(await sync_request.to_recon())

    async def receive_event(self, message: 'Envelope') -> None:
        await self.__set_value(message)

    async def receive_synced(self) -> None:
        self.synced.set()

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
        converter = RecordConverter.get_converter()
        self.value = converter.record_to_object(message.body, self.downlink_manager.registered_classes,
                                                self.downlink_manager.strict)

        await self.downlink_manager.subscribers_did_set(self.value, old_value)


class ValueDownlinkView(DownlinkView):

    def __init__(self, client: 'SwimClient') -> None:
        super().__init__(client)
        self.did_set_callback = None
        self.initialised = asyncio.Event()

    @property
    def value(self) -> 'Any':
        if self.model is None:
            return Value.absent()
        else:
            return self.model.value

    async def register_manager(self, manager: 'DownlinkManager') -> None:
        await self.assign_manager(manager)

        if manager.is_open:
            await self.execute_did_set(self.model.value, Value.absent())

        self.initialised.set()

    async def create_downlink_model(self, downlink_manager: 'DownlinkManager') -> 'ValueDownlinkModel':
        model = ValueDownlinkModel(self.client)
        await self.initalise_model(downlink_manager, model)
        return model

    @after_open
    def get(self, wait_sync: bool = False) -> Any:
        """
        Return the value of the downlink.

        :param wait_sync:       - If True, wait for the initial `sync` to be completed before returning.
                                  If False, return immediately.
        :return:                - The value of the Downlink.
        """
        if wait_sync:
            task = self.client.schedule_task(self.__get_value)
            return task.result()
        else:
            return self.value

    @after_open
    def set(self, value: Any, blocking: bool = False) -> None:
        """
        Send a command message to set the value of the lane on the remote agent to the given value.

        :param blocking:        - If True, block until the value has been sent to the server.
        :param value:           - New value for the lane of the remote agent.
        """
        task = self.client.schedule_task(self.send_message, value)

        if blocking:
            task.result()

    async def send_message(self, value: Any) -> None:
        """
        Send a message to the remote agent of the downlink.

        :param value:           - New value for the lane of the remote agent.
        """
        await self.initialised.wait()
        recon = RecordConverter.get_converter().object_to_record(value)
        message = CommandMessage(self.node_uri, self.lane_uri, recon)

        await self.model.send_message(message)

    def did_set(self, function: Callable) -> 'ValueDownlinkView':
        """
        Set the `did_set` callback of the current downlink view to a given function.

        :param function:   - Function to be called when a value is received by the downlink.
        :return:           - The current downlink view.
        """
        self.did_set_callback = validate_callback(function)
        return self

    # noinspection PyAsyncCall
    async def execute_did_set(self, current_value: Any, old_value: Any) -> None:
        """
        Execute the custom `did_set` callback of the current downlink view.

        :param current_value:       - The new value of the downlink.
        :param old_value:           - The previous value of the downlink.
        """
        if self.did_set_callback:
            self.client.schedule_task(self.did_set_callback, current_value, old_value)

    async def __get_value(self) -> 'Any':
        await self.initialised.wait()
        return await self.model.get_value()


class MapDownlinkModel(DownlinkModel):

    def __init__(self, client: 'SwimClient') -> None:
        super().__init__(client)
        self.map = {}
        self.synced = asyncio.Event()

    async def establish_downlink(self) -> None:
        sync_request = SyncRequest(self.node_uri, self.lane_uri)
        await self.connection.send_message(await sync_request.to_recon())

    async def receive_event(self, message: 'Envelope') -> None:
        if message.body.tag == 'update':
            await self.__receive_update(message)
        if message.body.tag == 'remove':
            await self.__receive_remove(message)

    async def receive_synced(self) -> None:
        self.synced.set()

    async def send_message(self, message: 'Envelope') -> None:
        """
        Send a message to the remote agent of the downlink.

        :param message:         - Message to send to the remote agent.
        """
        await self.linked.wait()
        await self.connection.send_message(await message.to_recon())

    async def get_value(self, key) -> Any:
        """
        Get a value from the map of the downlink using a given key, after it has been synced.

        :param key              - The key of the entry.
        :return:                - The current value of the downlink.
        """
        await self.synced.wait()
        return self.map.get(key, (Value.absent(), Value.absent()))[1]

    async def get_values(self) -> list:
        """
        Get all of the values from the map of the downlink as a list.

        :return:                - A list with all the values from the downlink map.
        """
        await self.synced.wait()
        return list(self.map.values())

    async def __receive_update(self, message: 'Envelope') -> None:
        key = RecordConverter.get_converter().record_to_object(message.body.get_head().value.get_head().value,
                                                               self.downlink_manager.registered_classes,
                                                               self.downlink_manager.strict)

        value = RecordConverter.get_converter().record_to_object(message.body.get_body(),
                                                                 self.downlink_manager.registered_classes,
                                                                 self.downlink_manager.strict)

        recon_key = await Recon.to_string(message.body.get_head().value.get_head().value)
        old_value = await self.get_value(recon_key)

        self.map[recon_key] = (key, value)
        await self.downlink_manager.subscribers_did_update(key, value, old_value)

    async def __receive_remove(self, message: 'Envelope') -> None:
        key = RecordConverter.get_converter().record_to_object(message.body.get_head().value.get_head().value,
                                                               self.downlink_manager.registered_classes,
                                                               self.downlink_manager.strict)

        recon_key = await Recon.to_string(message.body.get_head().value.get_head().value)
        old_value = self.map.pop(recon_key, (Value.absent(), Value.absent()))[1]

        await self.downlink_manager.subscribers_did_remove(key, old_value)


class MapDownlinkView(DownlinkView):

    def __init__(self, client: 'SwimClient') -> None:
        super().__init__(client)
        self.did_update_callback = None
        self.did_remove_callback = None
        self.initialised = asyncio.Event()

    async def register_manager(self, manager: 'DownlinkManager') -> None:
        await self.assign_manager(manager)

        if manager.is_open:
            for key, value in self.model.map.values():
                await self.execute_did_update(key, value, Value.absent())

        self.initialised.set()

    async def create_downlink_model(self, downlink_manager: 'DownlinkManager') -> 'MapDownlinkModel':
        model = MapDownlinkModel(self.client)
        await self.initalise_model(downlink_manager, model)
        return model

    def map(self, key: Any) -> [Value, dict]:
        if self.model is None:
            return Value.absent()
        else:
            if key is None:
                return list(self.model.map.values())
            else:
                return self.model.map.get(key, (Value.absent(), Value.absent()))[1]

    @after_open
    def get(self, key: Any, wait_sync: bool = False) -> Any:
        if wait_sync:
            task = self.client.schedule_task(self.__get_value, key)
            return task.result()
        else:
            return self.map(key)

    @after_open
    def get_all(self, wait_sync: bool = False) -> list:
        if wait_sync:
            task = self.client.schedule_task(self.__get_all_values)
            return task.result()
        else:
            return self.map(None)

    @after_open
    def put(self, key: Any, value: Any, blocking: bool = False) -> None:
        """
        Send a command message to put the given key and value in the remote map lane.

        :param key:             - Entry key.
        :param value:           - Entry value.
        :param blocking:        - If True, block until the value has been sent to the server.
        """
        task = self.client.schedule_task(self.__put_message, key, value)

        if blocking:
            task.result()

    @after_open
    def remove(self, key: Any, blocking: bool = False) -> None:
        """
        Send a command message to remove the given key from the remote map lane.

        :param key:             - Entry key.
        :param blocking:        - If True, block until the value has been sent to the server.
        """
        task = self.client.schedule_task(self.__remove_message, key)

        if blocking:
            task.result()

    def did_update(self, function: Callable) -> 'MapDownlinkView':
        """
        Set the `did_update` callback of the current downlink view to a given function.

        :param function:   - Function to be called when an update event is received by the downlink.
        :return:           - The current downlink view.
        """
        self.did_update_callback = validate_callback(function)
        return self

    # noinspection PyAsyncCall
    async def execute_did_update(self, key: Any, new_value: Any, old_value: Any) -> None:
        """
        Execute the custom `did_update` callback of the current downlink view.

        :param key:             - The entry key of the item.
        :param new_value:       - The new value of the item.
        :param old_value:       - The current value of the item.
        """
        if self.did_update_callback:
            self.client.schedule_task(self.did_update_callback, key, new_value, old_value)

    def did_remove(self, function: Callable) -> 'MapDownlinkView':
        """
        Set the `did_remove` callback of the current downlink view to a given function.

        :param function:   - Function to be called when a remove event is received by the downlink.
        :return:           - The current downlink view.
        """
        self.did_remove_callback = validate_callback(function)
        return self

    # noinspection PyAsyncCall
    async def execute_did_remove(self, key: Any, old_value: Any) -> None:
        """
        Execute the custom `did_remove` callback of the current downlink view.

        :param key:             - The entry key of the item.
        :param old_value:       - The current value of the item.
        """
        if self.did_remove_callback:
            self.client.schedule_task(self.did_remove_callback, key, old_value)

    async def __get_value(self, key: Any) -> Any:
        await self.initialised.wait()
        return await self.model.get_value(key)

    async def __get_all_values(self) -> list:
        await self.initialised.wait()
        return await self.model.get_values()

    async def __put_message(self, key: Any, value: Any) -> None:
        """
        Send a `put` message to the remote agent of the downlink.

        :param key:             - Key for the new entry in the map lane of the remote agent.
        :param value:           - Value for the new entry in the map lane of the remote agent.
        """
        await self.initialised.wait()

        message = CommandMessage(self.node_uri, self.lane_uri, UpdateRequest(key, value).to_record())
        await self.model.send_message(message)

    async def __remove_message(self, key: Any) -> None:
        """
        Send a `remove` message to the remote agent of the downlink.

        :param key:             - Key for the entry in the map lane that should be removed from the remote agent.
        """
        await self.initialised.wait()

        message = CommandMessage(self.node_uri, self.lane_uri, RemoveRequest(key).to_record())
        await self.model.send_message(message)
