import asyncio
import concurrent.futures
from threading import Thread
import websockets

from swimai.client.downlinks.value_downlink import ValueDownlink
from swimai.client.downlinks.ws_connection import WSConnection
from swimai.warp.warp import CommandMessage


class SwimClient:

    def __init__(self):
        self.downlinks = list()
        self.loop = None
        self.loop_thread = None
        self.websocket_connections = dict()
        self.executor = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.stop()
        return self

    def get_pool_executor(self):
        if self.executor is None:
            self.executor = concurrent.futures.ThreadPoolExecutor()

        return self.executor

    def downlink_value(self):
        return ValueDownlink(self)

    def command(self, host_uri, node_uri, lane_uri, body):
        message = CommandMessage(node_uri, lane_uri, body=body)
        self.schedule_task(self.__send_command, host_uri, message)

    async def __send_command(self, host_uri, message):
        await self.open_websocket(host_uri)
        await self.websocket_connections[host_uri].websocket.send(await message.to_recon())

    def start(self):
        loop = asyncio.new_event_loop()
        self.loop = loop

        self.loop_thread = Thread(target=self.__start_event_loop)
        self.loop_thread.start()

    def stop(self):
        self.schedule_task(self.__stop_client)
        self.loop_thread.join()

    def schedule_task(self, task, *args):

        if len(args) > 0:
            task = asyncio.run_coroutine_threadsafe(task(*args), loop=self.loop)
        else:
            task = asyncio.run_coroutine_threadsafe(task(), loop=self.loop)

        return task

    def unschedule_task(self, task):
        task.cancel()

    async def __stop_client(self):

        if self.executor is not None:
            self.executor.shutdown(wait=False)

        tasks = [task for task in asyncio.all_tasks(self.loop) if task is not asyncio.current_task(self.loop)]
        [task.cancel() for task in tasks]
        await asyncio.gather(*tasks, return_exceptions=True)

        self.loop.stop()

    def __start_event_loop(self):
        asyncio.set_event_loop(self.loop)
        asyncio.get_event_loop().run_forever()

    async def open_websocket(self, host_uri):
        try:
            if host_uri not in self.websocket_connections:
                connection = WSConnection(await websockets.connect(host_uri))
                self.websocket_connections[host_uri] = connection
            else:
                connection = self.websocket_connections[host_uri]
                connection.subscribe()
            return connection.websocket

        except Exception as e:
            print(e)

    async def remove_connection(self, host_uri):
        connection = self.websocket_connections.get(host_uri)
        connection.unsubscribe()

        if connection.subscribers == 0:
            await connection.websocket.close()
            self.websocket_connections.pop(host_uri)
