import websockets
from enum import Enum

from swimai.warp import Envelope


class ConnectionPool:

    def __init__(self) -> None:
        self.__connections = dict()

    @property
    def size(self):
        return len(self.__connections)

    async def get_connection(self, host_uri: str, caller) -> 'WSConnection':
        """
        Return a WebSocket connection to the given Host URI. If it is a new
        host, create the connection.

        :param host_uri:        - URI of the connection host.
        :return:                - WebSocket connection.
        """
        if host_uri not in self.__connections:
            connection = WSConnection(host_uri)
            self.__connections[host_uri] = connection
        else:
            connection = self.__connections.get(host_uri)

        await connection.subscribe(caller)
        return connection

    async def remove_connection(self, host_uri: str, caller) -> None:
        """
        Unsubscribe from a WebSocket connection. If the connection does not
        have any subscribers, close it and remove it from the pool.

        :param host_uri:        - URI of the connection host.
        """

        connection = self.__connections.get(host_uri)

        if connection:
            await connection.unsubscribe(caller)

            if connection.status == ConnectionStatus.CLOSED:
                self.__connections.pop(host_uri)


class WSConnection:

    def __init__(self, host_uri: str) -> None:
        self.host_uri = host_uri

        self.websocket = None
        self.status = ConnectionStatus.CLOSED
        self.__subscribers = SubscriberPool()

    def has_subscribers(self) -> bool:
        """
        Check if the connection has any subscribers.

        :return:        - True if there are subscribers. False otherwise.
        """
        return self.__subscribers.size > 0

    async def subscribe(self, subscriber) -> None:
        """
        Increment the number of subscribers to the connection.
        If this is the first subscriber, open the connection.
        """
        if self.__subscribers.size == 0:
            await self.__open()

        self.__subscribers.add_subscribers(subscriber)

    async def unsubscribe(self, subscriber) -> None:
        """
        Decrement the number of subscribers to the connection.
        If there are no subscribers, close the connection.
        """

        self.__subscribers.remove_subscriber(subscriber)
        if self.__subscribers.size == 0:
            await self.__close()

    async def __open(self) -> None:
        self.websocket = await websockets.connect(self.host_uri)
        self.status = ConnectionStatus.OPEN

    async def __close(self) -> None:
        if self.status == ConnectionStatus.OPEN:
            self.status = ConnectionStatus.CLOSED
            await self.websocket.close()

    async def wait_for_messages(self):
        self.status = ConnectionStatus.RUNNING
        try:
            while self.status == ConnectionStatus.RUNNING:
                message = await self.websocket.recv()
                response = await Envelope.parse_recon(message)
                await self.__subscribers.send_message(response)
        finally:
            await self.__close()


class ConnectionStatus(Enum):
    CLOSED = 0
    OPEN = 1
    RUNNING = 2


class SubscriberPool:

    def __init__(self):
        self.subscribers = dict()

    @property
    def size(self):
        return len(self.subscribers)

    def add_subscribers(self, subscriber):
        self.subscribers[hash(subscriber)] = subscriber

    def remove_subscriber(self, subscriber):
        self.subscribers.pop(hash(subscriber))

    async def send_message(self, message):
        for key, subscriber in self.subscribers.items():
            await subscriber.receive_message(message)


class Subscriber:

    def __init__(self, subscriber):
        self.subscriber = subscriber
