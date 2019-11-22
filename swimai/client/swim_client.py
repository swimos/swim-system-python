#  Copyright 2015-2019 SWIM.AI inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import asyncio
import inspect
import os
import sys
import traceback

from asyncio import Future, CancelledError
from threading import Thread
from typing import Callable, Any, Coroutine
from concurrent.futures.thread import ThreadPoolExecutor

from swimai.client.connections import ConnectionPool
from swimai.client.downlinks.downlinks import ValueDownlinkView
from swimai.client.utils import URI
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

        if exc_value or exc_traceback:
            self.handle_exception(exc_type, exc_value, exc_traceback)

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

    async def get_connection(self, host_uri: str):
        connection = await self.__connection_pool.get_connection(host_uri)
        return connection

    async def add_downlink_view(self, downlink):
        await self.__connection_pool.add_downlink_view(downlink)

    async def remove_downlink_view(self, downlink):
        await self.__connection_pool.remove_downlink_view(downlink)

    def exception_handler(self, feature):
        try:
            feature.result()
        except CancelledError:
            pass
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.handle_exception(exc_type, exc_value, exc_traceback)

    def handle_exception(self, exc_type, exc_value, exc_traceback):
        print(exc_value)
        traceback.print_tb(exc_traceback)

        if self.terminate_on_exception:
            os._exit(1)

        if self.execute_on_exception:
            self.schedule_task(self.execute_on_exception)

    def schedule_task(self, task: Callable[..., Coroutine], *args: Any) -> 'Future':

        if inspect.iscoroutinefunction(task):
            if len(args) > 0:
                task = asyncio.run_coroutine_threadsafe(task(*args), loop=self.loop)
            else:
                task = asyncio.run_coroutine_threadsafe(task(), loop=self.loop)
        else:
            if len(args) > 0:
                task = self.loop.run_in_executor(self.__get_pool_executor(), task, *args)
            else:
                task = self.loop.run_in_executor(self.__get_pool_executor(), task)

        task.add_done_callback(self.exception_handler)
        return task

    def downlink_value(self):
        return ValueDownlinkView(self)

    def command(self, host_uri: str, node_uri: str, lane_uri: str, body: 'Item') -> None:
        host_uri = URI.normalise_scheme(host_uri)
        message = CommandMessage(node_uri, lane_uri, body=body)
        self.schedule_task(self.__send_command, host_uri, message)

    async def __send_command(self, host_uri: str, message: 'Envelope') -> None:
        connection = await self.get_connection(host_uri)
        await connection.send_message(await message.to_recon())

    def __get_pool_executor(self) -> 'ThreadPoolExecutor':
        if self.executor is None:
            self.executor = ThreadPoolExecutor()

        return self.executor

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
