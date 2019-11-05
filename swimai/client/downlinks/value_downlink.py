import asyncio
from collections import Callable
import inspect

from swimai.structures.structs import Absent
from swimai.warp.warp import SyncRequest, CommandMessage, Envelope


class ValueDownlink:

    def __init__(self, client):
        self.client = client
        self.host_uri = None
        self.node_uri = None
        self.lane_uri = None
        self.websocket = None
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
        self.websocket = await self.client.open_websocket(self.host_uri)
        await self.establish_downlink()
        await self.receive_message()

    async def establish_downlink(self):

        sync_request = SyncRequest(self.node_uri, self.lane_uri)
        await self.websocket.send(await sync_request.to_recon())

    async def receive_message(self):
        try:
            while True:
                message = await self.websocket.recv()

                response = await Envelope.parse_recon(message)

                if response.tag == 'linked':
                    self.linked.set()
                elif response.tag == 'synced':
                    self.synced.set()
                elif response.tag == 'event':
                    await self.set_value(response)
        finally:
            await self.websocket.close()

    def get(self, blocking=False):

        if blocking:
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

        if inspect.iscoroutinefunction(self.execute_did_set):
            self.client.schedule_task(self.execute_did_set, self.value, old_value)
        else:
            self.client.loop.run_in_executor(self.client.get_pool_executor(), self.execute_did_set, self.value, old_value)

    async def send_message(self, message):
        await self.linked.wait()
        await self.websocket.send(await message.to_recon())

    def close(self):
        self.client.schedule_task(self.__close)

    async def __close(self):
        self.task.cancel()
        await self.client.remove_connection(self.host_uri)
