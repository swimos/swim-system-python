import asyncio
import inspect

from collections.abc import Callable

from swimai.client.utils import URI
from swimai.structures import Absent
from swimai.warp import SyncRequest, CommandMessage


class ValueDownlinkModel:

    def __init__(self, client):
        self.client = client
        self.host_uri = None
        self.node_uri = None
        self.lane_uri = None
        self.connection = None
        self.task = None
        self.downlink = None

        self.value = None

        self.linked = asyncio.Event(loop=self.client.loop)
        self.synced = asyncio.Event(loop=self.client.loop)

    async def establish_downlink(self):
        sync_request = SyncRequest(self.node_uri, self.lane_uri)
        await self.connection.send_message(await sync_request.to_recon())

    async def receive_message(self, message):

        if message.tag == 'linked':
            self.linked.set()
        elif message.tag == 'synced':
            self.synced.set()
        elif message.tag == 'event':
            await self.set_value(message)

    def get(self, synchronous=False):
        if synchronous:
            task = self.client.schedule_task(self.get_val)
            return task.result()
        else:
            return self.value

    async def get_val(self):
        await self.synced.wait()
        return self.value

    async def set_value(self, response):
        old_value = self.value

        if response.body == Absent.get_absent():
            self.value = None
        else:
            self.value = response.body.value

        await self.downlink.subscribers_did_set(self.value, old_value)

    def open(self):
        self.task = self.client.schedule_task(self.connection.wait_for_messages)
        return self

    async def send_message(self, message):
        await self.synced.wait()
        await self.connection.send_message(await message.to_recon())

    def close(self):
        self.client.schedule_task(self.__close)

    async def __close(self):
        self.task.cancel()


class ValueDownlinkView:

    def __init__(self, client):
        self.client = client
        self.host_uri = None
        self.node_uri = None
        self.lane_uri = None
        self.is_open = False

        self.initialised = asyncio.Event(loop=self.client.loop)
        self.model = None
        self.connection = None

    @property
    def route(self):
        return f'{self.node_uri}/{self.lane_uri}'

    def open(self):

        if not self.is_open:
            self.is_open = True
            self.client.schedule_task(self.client.add_downlink_view, self)

        return self

    def close(self):

        if self.is_open:
            self.is_open = False
            self.client.schedule_task(self.client.remove_downlink_view, self)

        return self

    async def establish_downlink(self):
        await self.model.establish_downlink()

    async def create_downlink_model(self):
        model = ValueDownlinkModel(self.client)
        model.host_uri = self.host_uri
        model.node_uri = self.node_uri
        model.lane_uri = self.lane_uri

        return model

    def set_host_uri(self, host_uri):
        self.host_uri = URI.normalise_scheme(host_uri)
        return self

    def set_node_uri(self, node_uri):
        self.node_uri = node_uri
        return self

    def set_lane_uri(self, lane_uri):
        self.lane_uri = lane_uri
        return self

    async def did_set_callback(self, new_value, old_value):
        pass

    def did_set(self, function):

        if inspect.iscoroutinefunction(function):
            self.did_set_callback = function
        elif isinstance(function, Callable):
            self.did_set_callback = function
        else:
            raise TypeError('Callback must be a function!')

        return self

    async def execute_did_set(self, current_value, old_value):
        self.client.schedule_task(self.did_set_callback, current_value, old_value)

    def set(self, value):
        if self.is_open:
            message = CommandMessage(self.node_uri, self.lane_uri, value)
            self.client.schedule_task(self.send_message, message)
        else:
            raise RuntimeError('Link is not open!')

    async def send_message(self, message):
        await self.initialised.wait()
        await self.model.send_message(message)

    def get(self, synchronous=False):
        if self.is_open:
            return self.model.get(synchronous)
        else:
            raise RuntimeError('Link is not open!')
