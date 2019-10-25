import asyncio
from threading import Thread

import websockets

from swim.client.downlinks.value_downlink import ValueDownlink
from swim.warp.warp import CommandMessage


class SwimClient:

    def __init__(self):
        self.downlinks = list()
        self.loop = None
        self.websocket_pool = dict()

    def downlink_value(self):
        return ValueDownlink(self)

    def command(self, host_uri, node_uri, lane_uri, body):
        message = CommandMessage(node_uri, lane_uri, body=body)
        self.schedule_task(self.__send_command, host_uri, message)

    async def __send_command(self, host_uri, message):
        await self.open_websocket(host_uri)
        await self.websocket_pool[host_uri].send(await message.to_recon())

    def start(self):
        loop = asyncio.new_event_loop()
        self.loop = loop

        thread = Thread(target=self.__start_event_loop)
        thread.start()

    def stop(self):
        self.schedule_task(self.__stop_client)

    def schedule_task(self, task, *args):

        if len(args) > 0:
            asyncio.run_coroutine_threadsafe(task(*args), loop=self.loop)
        else:
            asyncio.run_coroutine_threadsafe(task(), loop=self.loop)

    def unschedule_task(self, task):
        task.cancel()

    async def __stop_client(self):
        tasks = [task for task in asyncio.all_tasks(self.loop) if task is not asyncio.current_task(self.loop)]
        [task.cancel() for task in tasks]
        await asyncio.gather(*tasks, return_exceptions=True)

        self.loop.stop()

    def __start_event_loop(self):
        asyncio.set_event_loop(self.loop)
        asyncio.get_event_loop().run_forever()

    async def open_websocket(self, host_uri):
        try:
            if host_uri not in self.websocket_pool:
                self.websocket_pool[host_uri] = await websockets.connect(host_uri)

            return self.websocket_pool[host_uri]
        
        except Exception as e:
            print(e)
