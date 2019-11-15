from enum import Enum

import websockets
from websockets import WebSocketClientProtocol


class ConnectionPool:

    def __init__(self) -> None:
        self.connections = dict()

    async def get_connection(self, host_uri: str) -> 'WebSocketClientProtocol':
        """
        Return a WebSocket connection to the given Host URI. If it is a new
        host, create the connection.

        :param host_uri:        - URI of the connection host.
        :return:                - WebSocket connection.
        """
        if host_uri not in self.connections:
            connection = WSConnection(host_uri)
            self.connections[host_uri] = connection
        else:
            connection = self.connections.get(host_uri)

        await connection.subscribe()
        return connection.websocket

    # TODO: Add guard here
    async def remove_connection(self, host_uri: str) -> None:
        """
        Unsubscribe from a WebSocket connection. If the connection does not
        have any subscribers, close it and remove it from the pool.

        :param host_uri:        - URI of the connection host.
        """

        connection = self.connections.get(host_uri)
        await connection.unsubscribe()

        if connection.status == ConnectionStatus.CLOSED:
            self.connections.pop(host_uri)


class WSConnection:

    def __init__(self, host_uri: str) -> None:
        self.host_uri = host_uri

        self.websocket = None
        self.status = ConnectionStatus.CLOSED
        self.__subscribers = 0

    def has_subscribers(self) -> bool:
        """
        Check if the connection has any subscribers.

        :return:        - True if there are subscribers. False otherwise.
        """
        return self.__subscribers > 0

    async def subscribe(self) -> None:
        """
        Increment the number of subscribers to the connection.
        If this is the first subscriber, open the connection.
        """
        if self.__subscribers == 0:
            await self.__open()

        self.__subscribers += 1

    async def unsubscribe(self) -> None:
        """
        Decrement the number of subscribers to the connection.
        If there are no subscribers, close the connection.
        """

        self.__subscribers -= 1
        if self.__subscribers == 0:
            await self.__close()

    async def __open(self) -> None:
        self.websocket = await websockets.connect(self.host_uri)
        self.status = ConnectionStatus.OPEN

    async def __close(self) -> None:

        if self.status == ConnectionStatus.OPEN:
            await self.websocket.close()
            self.status = ConnectionStatus.CLOSED


class ConnectionStatus(Enum):
    CLOSED = 0
    OPEN = 1
