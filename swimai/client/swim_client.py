import asyncio
import concurrent.futures
from threading import Thread

from swimai.client.downlinks import ValueDownlink
from swimai.client.connections import ConnectionPool
from swimai.warp import CommandMessage


class SwimClient:

    def __init__(self) -> None:
        self.loop = None
        self.loop_thread = None
        self.executor = None
        self.__connection_pool = ConnectionPool()

    def __enter__(self) -> 'SwimClient':
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback) -> 'SwimClient':
        self.stop()
        return self

    def start(self):
        loop = asyncio.new_event_loop()
        self.loop = loop

        self.loop_thread = Thread(target=self.__start_event_loop)
        self.loop_thread.start()

    def stop(self):
        self.schedule_task(self.__stop_event_loop)
        self.loop_thread.join()

    # May throw exception
    async def get_connection(self, host_uri):
        return await self.__connection_pool.get_connection(host_uri)

    async def remove_connection(self, host_uri):
        return await self.__connection_pool.remove_connection(host_uri)

    def schedule_task(self, task, *args):
        if len(args) > 0:
            task = asyncio.run_coroutine_threadsafe(task(*args), loop=self.loop)
        else:
            task = asyncio.run_coroutine_threadsafe(task(), loop=self.loop)

        return task

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
        connection = await self.get_connection(host_uri)
        await connection.send(await message.to_recon())

    def __start_event_loop(self):
        asyncio.set_event_loop(self.loop)
        asyncio.get_event_loop().run_forever()

    async def __stop_event_loop(self):

        if self.executor is not None:
            self.executor.shutdown(wait=False)

        tasks = [task for task in asyncio.all_tasks(self.loop) if task is not asyncio.current_task(self.loop)]
        [task.cancel() for task in tasks]
        await asyncio.gather(*tasks, return_exceptions=True)

        self.loop.stop()

    # @staticmethod
    # def unschedule_task(task):
    #     task.cancel()
