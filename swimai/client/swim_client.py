import asyncio
import inspect
import os

from asyncio import Future
from threading import Thread
from typing import Callable, Any
from concurrent.futures.thread import ThreadPoolExecutor

from swimai.client.downlinks import ValueDownlink
from swimai.client.connections import ConnectionPool
from swimai.structures import Item
from swimai.warp import CommandMessage, Envelope


class SwimClient:

    def __init__(self, terminate_on_exception=False, execute_on_exception=None) -> None:
        self.loop = None
        self.loop_thread = None
        self.executor = None
        self.__connection_pool = ConnectionPool()

        self.execute_on_exception = execute_on_exception
        self.terminate_on_exception = terminate_on_exception

    def __enter__(self) -> 'SwimClient':
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback) -> 'SwimClient':
        self.stop()
        return self

    def start(self) -> None:
        loop = asyncio.new_event_loop()
        self.loop = loop
        self.loop_thread = Thread(target=self.__start_event_loop)
        self.loop_thread.start()

    def stop(self) -> None:
        self.schedule_task(self.__stop_event_loop)
        self.loop_thread.join()
        self.loop.close()

    async def get_connection(self, host_uri: str, caller):
        try:
            connection = await self.__connection_pool.get_connection(host_uri, caller)
            return connection

        except Exception as exception:
            print(f'Unable to establish connection to {host_uri}\n{str(exception)}')

            if self.terminate_on_exception:
                os._exit(1)

            await self.remove_connection(host_uri, caller)

            if self.execute_on_exception:
                await self.schedule_task(self.execute_on_exception)

    async def remove_connection(self, host_uri: str, caller) -> None:
        await self.__connection_pool.remove_connection(host_uri, caller)

    def schedule_task(self, task: Callable[..., 'Coroutine'], *args: Any) -> 'Future':

        if inspect.iscoroutinefunction(task):
            if len(args) > 0:
                task = asyncio.run_coroutine_threadsafe(task(*args), loop=self.loop)
            else:
                task = asyncio.run_coroutine_threadsafe(task(), loop=self.loop)
        else:
            if len(args) > 0:
                self.loop.run_in_executor(self.get_pool_executor(), task, *args)
            else:
                self.loop.run_in_executor(self.get_pool_executor(), task)

        return task

    def get_pool_executor(self) -> 'ThreadPoolExecutor':
        if self.executor is None:
            self.executor = ThreadPoolExecutor()

        return self.executor

    def downlink_value(self) -> 'ValueDownlink':
        return ValueDownlink(self)

    def command(self, host_uri: str, node_uri: str, lane_uri: str, body: 'Item') -> None:
        message = CommandMessage(node_uri, lane_uri, body=body)
        self.schedule_task(self.__send_command, host_uri, message)

    async def __send_command(self, host_uri: str, message: 'Envelope') -> None:
        websocket = await self.get_connection(host_uri, self)

        if websocket:
            await websocket.send(await message.to_recon())

    def __start_event_loop(self) -> None:
        asyncio.set_event_loop(self.loop)
        asyncio.get_event_loop().run_forever()

    async def __stop_event_loop(self):

        if self.executor is not None:
            self.executor.shutdown(wait=False)

        tasks = [task for task in asyncio.all_tasks(self.loop) if task is not asyncio.current_task(self.loop)]
        [task.cancel() for task in tasks]
        await asyncio.gather(*tasks, return_exceptions=True)

        self.loop.stop()
