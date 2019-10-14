import asyncio
import concurrent.futures
import inspect

from swimai.warp.sync_request import SyncRequest


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

    # async def async_wrapper(self, function, *args):
    #     await function(*args)

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
        self.execute_did_set = function
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
            response = await self.client.websocket.recv()

            # TODO define parser to handle the decoding of messages

            if 'event' in response:
                data = response.split(')')

                if len(data) > 1:
                    old_value = self.value
                    self.value = data[1]

                    if inspect.iscoroutinefunction(self.execute_did_set):
                        self.client.schedule_task(self.execute_did_set, self.value, old_value)
                    else:
                        self.client.loop.run_in_executor(self.executor, self.execute_did_set, self.value, old_value)
                    # Schedule a task
                    # self.execute_did_set(self.value, old_value)
            if 'linked' in response:
                self.linked.set()

            # if command == 'linked':
            #     did_link()
            # if command == 'synced':
            #     did_sync()
            # if command == 'event':
            #     execute_did_set()

    def get(self):
        pass

    def set(self, value):
        message = self.create_set_message(value, self.node_uri, self.lane_uri)
        self.client.schedule_task(self.send_message, message)

    async def send_message(self, message):
        await self.linked.wait()
        await self.client.websocket.send(message)

    def create_set_message(self, value, node_uri, lane_uri):
        return f'@command(node:"{node_uri}",lane:{lane_uri})"{value}"'
