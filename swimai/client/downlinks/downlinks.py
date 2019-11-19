import asyncio
import inspect

from collections.abc import Callable
from swimai.structures import Absent
from swimai.warp import SyncRequest, CommandMessage


class ValueDownlinkView:
    pass


class ValueDownlinkModel:

    def __init__(self, client):
        self.client = client
        self.host_uri = None
        self.node_uri = None
        self.lane_uri = None
        self.connection = None
        self.task = None
        self.value = None

        self.linked = asyncio.Event(loop=self.client.loop)
        self.synced = asyncio.Event(loop=self.client.loop)

    def execute_did_set(self, new_value, old_value):
        # no-op
        pass

    def set_host_uri(self, host_uri):
        self.host_uri = host_uri
        return self

    def set_node_uri(self, node_uri):
        self.node_uri = node_uri
        return self

    def set_lane_uri(self, lane_uri):
        self.lane_uri = lane_uri
        return self

    def did_set(self, function):

        if inspect.iscoroutinefunction(function):
            self.execute_did_set = function
        elif isinstance(function, Callable):
            self.execute_did_set = function
        else:
            raise TypeError('Callback must be a function!')

        return self

    def open(self):
        self.task = self.client.schedule_task(self.__open)
        return self

    async def __open(self):
        self.connection = await self.client.get_connection(self.host_uri, self)
        await self.establish_downlink()
        self.client.schedule_task(self.connection.wait_for_messages)

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

    def set(self, value):
        message = CommandMessage(self.node_uri, self.lane_uri, value)
        self.client.schedule_task(self.send_message, message)

    async def set_value(self, response):
        old_value = self.value

        if response.body == Absent.get_absent():
            self.value = None
        else:
            self.value = response.body.value

        self.client.schedule_task(self.execute_did_set, self.value, old_value)

    async def send_message(self, message):
        await self.synced.wait()
        await self.connection.send_message(await message.to_recon())

    def close(self):
        self.client.schedule_task(self.__close)

    async def __close(self):
        self.task.cancel()
        await self.client.remove_connection(self.host_uri, self)
