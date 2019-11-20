import websockets
from enum import Enum
from urllib.parse import urlparse
from swimai.warp import Envelope


class ConnectionPool:

    def __init__(self) -> None:
        self.__connections = dict()

    @property
    def size(self):
        return len(self.__connections)

    async def get_connection(self, host_uri: str, caller=None) -> 'WSConnection':
        """
        Return a WebSocket connection to the given Host URI. If it is a new
        host, create the connection.

        :param host_uri:        - URI of the connection host.
        :return:                - WebSocket connection.
        """
        if host_uri not in self.__connections:
            connection = WSConnection(host_uri)

            if caller:
                await connection.subscribe(caller)

            self.__connections[host_uri] = connection
        else:
            connection = self.__connections.get(host_uri)
            if caller:
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

    async def add_downlink_view(self, downlink_view):
        host_uri = downlink_view.host_uri

        if host_uri in self.__connections:
            connection = self.__connections.get(host_uri)
        else:
            connection = WSConnection(host_uri)

        downlink_view.connection = connection
        await connection.subscribe(downlink_view)


class WSConnection:

    def __init__(self, host_uri: str) -> None:
        self.host_uri = host_uri

        self.websocket = None
        self.status = ConnectionStatus.CLOSED
        self.__subscribers = DownlinkPool()

    @property
    def host_uri(self):
        return self.__host_uri

    @host_uri.setter
    def host_uri(self, uri):
        uri = urlparse(uri)
        if self.has_valid_scheme(uri):
            uri = uri._replace(scheme='ws')
            self.__host_uri = uri.geturl()
        else:
            raise TypeError('Invalid scheme for URI!')

    def has_valid_scheme(self, uri):
        scheme = uri.scheme
        return scheme == 'ws' or scheme == 'warp'

    def has_subscribers(self) -> bool:
        """
        Check if the connection has any subscribers.

        :return:        - True if there are subscribers. False otherwise.
        """
        return self.__subscribers.size > 0

    async def send_message(self, message):

        if self.websocket is None:
            await self.__open()

        await self.websocket.send(message)

    async def subscribe(self, downlink_view) -> None:
        """
        Increment the number of subscribers to the connection.
        If this is the first subscriber, open the connection.
        """
        if self.__subscribers.size == 0:
            await self.__open()

        await self.__subscribers.add_downlink(downlink_view, self)

    async def unsubscribe(self, downlink) -> None:
        """
        Decrement the number of subscribers to the connection.
        If there are no subscribers, close the connection.
        """

        self.__subscribers.remove_downlink(downlink)
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
        if self.status != ConnectionStatus.RUNNING:
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


class DownlinkPool:

    def __init__(self):
        self.downlinks = dict()

    @property
    def size(self):
        return len(self.downlinks)

    async def add_downlink(self, downlink_view, connection):

        if downlink_view.route in self.downlinks:
            downlink = self.downlinks.get(downlink_view.route)
        else:
            downlink = Downlink(connection)
            await downlink.init_downlink_model(downlink_view)
            self.downlinks[downlink_view.route] = downlink

        await downlink.register_view(downlink_view)

    def remove_downlink(self, downlink):
        # TODO count number of views before removing
        self.downlinks.pop(downlink.route)

    async def send_message(self, message):
        # TODO send based on lane and node URIs
        for key, downlink in self.downlinks.items():
            await downlink.receive_message(message)


class Downlink:

    def __init__(self, connection):
        self.connection = connection
        self.downlink_model = None
        self.views = dict()

    async def subscribers_did_set(self, current_value, old_value):
        for key, view in self.views.items():
            await view.execute_did_set(current_value, old_value)

    async def init_downlink_model(self, downlink_view):
        self.downlink_model = await downlink_view.create_downlink_model()
        self.downlink_model.downlink = self
        self.downlink_model.connection = self.connection
        await self.downlink_model.establish_downlink()
        self.downlink_model.open()

    async def register_view(self, downlink_view):
        downlink_view.model = self.downlink_model
        self.views[hash(downlink_view)] = downlink_view

    async def receive_message(self, message):
        await self.downlink_model.receive_message(message)
