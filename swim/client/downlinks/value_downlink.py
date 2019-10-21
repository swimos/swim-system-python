import asyncio
from collections import Callable
import concurrent.futures
import inspect

from swim.structures.structs import Absent
from swim.warp.warp import SyncRequest, CommandMessage, Envelope


class ValueDownlink:

    def __init__(self, client):
        self.client = client
        self.host_uri = None
        self.node_uri = None
        self.lane_uri = None

        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

        self.value = None
        self.linked = asyncio.Event(loop=self.client.loop)

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
        self.client.schedule_task(self.__open)
        return self

    async def __open(self):
        await self.client.open_websocket(self.host_uri)
        await self.establish_downlink()
        await self.receive_message()

    async def establish_downlink(self):

        sync_request = SyncRequest(self.node_uri, self.lane_uri)
        await self.client.websocket.send(await sync_request.to_recon())

    async def receive_message(self):
        while True:
            message = await self.client.websocket.recv()

            response = await Envelope.parse_recon(message)

            if response.tag == 'linked':
                self.linked.set()
            elif response.tag == 'synced':
                pass
            elif response.tag == 'event':
                await self.set_value(response)

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
            self.client.loop.run_in_executor(self.executor, self.execute_did_set, self.value, old_value)

    async def send_message(self, message):
        await self.linked.wait()
        await self.client.websocket.send(await message.to_recon())
