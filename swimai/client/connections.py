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
from typing import TYPE_CHECKING
from swimai.warp import Envelope

if TYPE_CHECKING:
    from .downlinks import ValueDownlinkView


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
        connection: WSConnection

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
        self.__subscribers = DownlinkPool()

    async def open(self) -> None:
        if self.status == ConnectionStatus.CLOSED:
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

        await self.__subscribers.add_downlink(downlink_view, self)

    async def unsubscribe(self, downlink_view: 'ValueDownlinkView') -> None:
        """
        Remove a downlink view from the subscriber list of the current connection.
        If there are no other subscribers, close the connection.

        :param downlink_view:   - Downlink view to remove from the subscribers.
        """

        await self.__subscribers.remove_downlink(downlink_view)
        if not self.has_subscribers():
            await self.close()

    async def send_message(self, message: str) -> None:
        """
        Send a string message to the host using a WebSocket connection.
        If the WebSocket connection to the host is not open, open it.

        :param message:         - String message to send to the remote host.
        """
        if self.websocket is None or self.status == ConnectionStatus.CLOSED:
            await self.open()

        await self.websocket.send(message)

    async def wait_for_messages(self) -> None:
        """
        Wait for messages from the remote host and propagate them
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
    IDLE = 1
    RUNNING = 2


class DownlinkPool:

    def __init__(self):
        self.downlinks = dict()

    @property
    def size(self):
        return len(self.downlinks)

    async def add_downlink(self, downlink_view, connection):

        downlink = self.downlinks.get(downlink_view.route)

        if downlink is None:
            downlink = Downlink(connection)
            self.downlinks[downlink_view.route] = downlink

        await downlink.add_view(downlink_view)

    async def remove_downlink(self, downlink_view):

        if downlink_view.route in self.downlinks:
            downlink = self.downlinks.get(downlink_view.route)
            await downlink.remove_view(downlink_view)

            if downlink.view_count == 0:
                self.downlinks.pop(downlink_view.route)

    async def receive_message(self, message):

        downlink = self.downlinks.get(message.route)
        if downlink:
            await downlink.receive_message(message)


class Downlink:

    def __init__(self, connection):
        self.connection = connection
        self.downlink_model = None
        self.downlink_views = dict()

    @property
    def view_count(self):
        return len(self.downlink_views)

    async def subscribers_did_set(self, current_value, old_value):
        for view in self.downlink_views.values():
            await view.execute_did_set(current_value, old_value)

    async def add_view(self, downlink_view):

        if self.downlink_model is None:
            await self.__init_downlink_model(downlink_view)
            await self.__open()

        downlink_view.model = self.downlink_model
        downlink_view.initialised.set()
        self.downlink_views[hash(downlink_view)] = downlink_view

    async def remove_view(self, downlink_view):

        if hash(downlink_view) in self.downlink_views:
            self.downlink_views.pop(hash(downlink_view))

            if self.view_count == 0:
                await self.__close()

    async def receive_message(self, message):
        await self.downlink_model.receive_message(message)

    async def __init_downlink_model(self, downlink_view):
        self.downlink_model = await downlink_view.create_downlink_model()
        self.downlink_model.downlink = self
        self.downlink_model.connection = self.connection

    async def __open(self):
        await self.downlink_model.establish_downlink()
        self.downlink_model.open()

    async def __close(self):
        self.downlink_model.close()
