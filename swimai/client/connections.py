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

import websockets
from enum import Enum

from swimai.warp import Envelope
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .downlinks import ValueDownlinkView
    from .downlinks import ValueDownlinkModel


class ConnectionPool:

    def __init__(self) -> None:
        self.__connections = dict()

    @property
    def size(self):
        return len(self.__connections)

    async def get_connection(self, host_uri: str) -> 'WSConnection':
        """
        Return a WebSocket connection to the given Host URI. If it is a new
        host or the existing connection is closing, create a new connection.

        :param host_uri:        - URI of the connection host.
        :return:                - WebSocket connection.
        """

        connection = self.__connections.get(host_uri)

        if connection is None or connection.status == ConnectionStatus.CLOSED:
            connection = WSConnection(host_uri)
            self.__connections[host_uri] = connection

        return connection

    async def remove_connection(self, host_uri: str) -> None:
        """
        Remove a connection from the pool.

        :param host_uri:        - URI of the connection host.
        """

        connection = self.__connections.get(host_uri)

        if connection:
            self.__connections.pop(host_uri)
            await connection.close()

    async def add_downlink_view(self, downlink_view: 'ValueDownlinkView') -> None:
        """
        Subscribe a downlink view to a connection from the pool.

        :param downlink_view:   - Downlink view to subscribe to a connection.
        """

        host_uri = downlink_view.host_uri
        connection = await self.get_connection(host_uri)
        downlink_view.connection = connection

        await connection.subscribe(downlink_view)

    async def remove_downlink_view(self, downlink_view: 'ValueDownlinkView') -> None:
        """
        Unsubscribe a downlink view from a connection from the pool.

        :param downlink_view:   - Downlink view to unsubscribe from a connection.
        """
        connection: 'WSConnection'

        host_uri = downlink_view.host_uri
        connection = self.__connections.get(host_uri)

        if connection:
            await connection.unsubscribe(downlink_view)

            if connection.status == ConnectionStatus.CLOSED:
                await self.remove_connection(host_uri)


class WSConnection:

    def __init__(self, host_uri: str) -> None:
        self.host_uri = host_uri

        self.websocket = None
        self.status = ConnectionStatus.CLOSED
        self.__subscribers = DownlinkManagerPool()

    async def open(self) -> None:
        if self.status == ConnectionStatus.CLOSED:
            self.status = ConnectionStatus.CONNECTING
            self.websocket = await websockets.connect(self.host_uri)
            self.status = ConnectionStatus.IDLE

    async def close(self) -> None:
        if self.status != ConnectionStatus.CLOSED:
            self.status = ConnectionStatus.CLOSED

            if self.websocket:
                await self.websocket.close()

    def has_subscribers(self) -> bool:
        """
        Check if the connection has any subscribers.

        :return:        - True if there are subscribers. False otherwise.
        """
        return self.__subscribers.size > 0

    async def subscribe(self, downlink_view: 'ValueDownlinkView') -> None:
        """
        Add a downlink view to the subscriber list of the current connection.
        If this is the first subscriber, open the connection.

        :param downlink_view:   - Downlink view to add to the subscribers.
        """
        if self.__subscribers.size == 0:
            await self.open()

        await self.__subscribers.register_downlink_view(downlink_view)

    async def unsubscribe(self, downlink_view: 'ValueDownlinkView') -> None:
        """
        Remove a downlink view from the subscriber list of the current connection.
        If there are no other subscribers, close the connection.

        :param downlink_view:   - Downlink view to remove from the subscribers.
        """

        await self.__subscribers.deregister_downlink_view(downlink_view)
        if not self.has_subscribers():
            await self.close()

    async def send_message(self, message: str) -> None:
        """
        Send a string message to the host using a WebSocket connection.
        If the WebSocket connection to the host is not open, open it.

        :param message:         - String message to send to the remote agent.
        """
        if self.websocket is None or self.status == ConnectionStatus.CLOSED:
            await self.open()

        await self.websocket.send(message)

    async def wait_for_messages(self) -> None:
        """
        Wait for messages from the remote agent and propagate them
        to all subscribers.
        """

        if self.status == ConnectionStatus.IDLE:
            self.status = ConnectionStatus.RUNNING
            try:
                while self.status == ConnectionStatus.RUNNING:
                    message = await self.websocket.recv()
                    response = await Envelope.parse_recon(message)
                    await self.__subscribers.receive_message(response)
            finally:
                await self.close()


class ConnectionStatus(Enum):
    CLOSED = 0
    CONNECTING = 1
    IDLE = 2
    RUNNING = 3


class DownlinkManagerPool:

    def __init__(self) -> None:
        self.__downlink_managers = dict()

    @property
    def size(self) -> int:
        return len(self.__downlink_managers)

    async def register_downlink_view(self, downlink_view: 'ValueDownlinkView') -> None:
        """
        Add a downlink view to a downlink manager from the pool with the given node and lane URIs.
        If a downlink manager is not yet created for the given node and lane, create it and add the downlink view.


        :param downlink_view:   - Downlink view to add to a corresponding downlink manager.
        """
        downlink_manager = self.__downlink_managers.get(downlink_view.route)

        if downlink_manager is None:
            downlink_manager = DownlinkManager(downlink_view.connection)
            self.__downlink_managers[downlink_view.route] = downlink_manager

        await downlink_manager.add_view(downlink_view)

    async def deregister_downlink_view(self, downlink_view: 'ValueDownlinkView') -> None:
        """
        Remove a downlink view from the corresponding downlink manager if it exists.
        If it is the last downlink view in the given manager, remove the manager from the pool.

        :param downlink_view:   - Downlink view to remove from the corresponding downlink manager.
        """
        downlink_manager: DownlinkManager

        if downlink_view.route in self.__downlink_managers:
            downlink_manager = self.__downlink_managers.get(downlink_view.route)
            await downlink_manager.remove_view(downlink_view)

            if downlink_manager.view_count == 0:
                self.__downlink_managers.pop(downlink_view.route)

    async def receive_message(self, message: 'Envelope') -> None:
        """
        Route a received message for the given host URI to the downlink manager for the corresponding
        node and lane URIs.

        :param message:         - Message received from the remote agent.
        """
        downlink_manager: DownlinkManager

        downlink_manager = self.__downlink_managers.get(message.route)
        if downlink_manager:
            await downlink_manager.receive_message(message)


class DownlinkManager:

    def __init__(self, connection: 'WSConnection') -> None:
        self.connection = connection
        self.status = DownlinkManagerStatus.CLOSED
        self.downlink_model = None
        self.__downlink_views = dict()

    @property
    def view_count(self) -> int:
        return len(self.__downlink_views)

    async def open(self) -> None:
        self.downlink_model: ValueDownlinkModel

        if self.status == DownlinkManagerStatus.CLOSED:
            self.status = DownlinkManagerStatus.OPENING
            self.downlink_model.open()
            await self.downlink_model.establish_downlink()
            self.status = DownlinkManagerStatus.OPEN

    async def close(self) -> None:
        self.downlink_model: ValueDownlinkModel

        if self.status != DownlinkManagerStatus.CLOSED:
            self.status = DownlinkManagerStatus.CLOSED
            self.downlink_model.close()

    async def init_downlink_model(self, downlink_view: 'ValueDownlinkView') -> None:
        """
        Initialise a downlink model to the specified node and lane of the remote agent.

        :param downlink_view:       - Downlink view with the information about the remote agent.
        """
        self.downlink_model = await downlink_view.create_downlink_model()
        self.downlink_model.downlink = self
        self.downlink_model.connection = self.connection

    async def add_view(self, downlink_view: 'ValueDownlinkView') -> None:
        """
        Add a downlink view to the manager. If a downlink model is not yet created, create it and open it.

        :param downlink_view:       - Downlink view to add to the manager.
        """
        if self.downlink_model is None:
            await self.init_downlink_model(downlink_view)

        downlink_view.model = self.downlink_model
        downlink_view.initialised.set()

        if self.view_count == 0:
            await self.open()

        self.__downlink_views[hash(downlink_view)] = downlink_view

    async def remove_view(self, downlink_view: 'ValueDownlinkView') -> None:
        """
        Remove a downlink view from the manager. If it is the last view associated with the manager,
        close the manager.

        :param downlink_view:       - Downlink view to remove from the manager.
        """
        if hash(downlink_view) in self.__downlink_views:
            self.__downlink_views.pop(hash(downlink_view))

            if self.view_count == 0:
                await self.close()

    async def receive_message(self, message: 'Envelope') -> None:
        """
        Send a received message to the downlink model.

        :param message:             - Received message from the remote agent.
        """
        self.downlink_model: ValueDownlinkModel

        await self.downlink_model.receive_message(message)

    async def subscribers_did_set(self, current_value: Any, old_value: Any) -> None:
        """
        Execute the `did_set` method of all downlink views of the downlink manager.

        :param current_value:       - The new value of the downlink.
        :param old_value:           - The previous value of the downlink.
        """
        for view in self.__downlink_views.values():
            await view.execute_did_set(current_value, old_value)


class DownlinkManagerStatus(Enum):
    CLOSED = 0
    OPENING = 1
    OPEN = 2
