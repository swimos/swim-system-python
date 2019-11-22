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
from traceback import TracebackException
from typing import Callable, Any, Optional
from concurrent.futures.thread import ThreadPoolExecutor
from .connections import ConnectionPool, WSConnection
from .downlinks import ValueDownlinkView
from .utils import URI
from swimai.structures import Item
from swimai.warp import CommandMessage, Envelope


class SwimClient:

    def __init__(self, terminate_on_exception: bool = False, execute_on_exception: Callable = None) -> None:
        self.loop = None
        self.loop_thread = None
        self.executor = None
        self.__connection_pool = ConnectionPool()

        self.execute_on_exception = execute_on_exception
        self.terminate_on_exception = terminate_on_exception

    def __enter__(self) -> 'SwimClient':
        self.start()
        return self

    def __exit__(self, exc_type: Optional[type], exc_value: Optional[Exception],
                 exc_traceback: Optional[TracebackException]) -> 'SwimClient':

        if exc_value or exc_traceback:
            self.__handle_exception(exc_value, exc_traceback)

        self.stop()
        return self

    def start(self) -> 'SwimClient':
        """
        Start the Swim client.
        Create a new thread and starts an asyncio loop inside it.
        """
        loop = asyncio.new_event_loop()
        self.loop = loop
        self.loop_thread = Thread(target=self.__start_event_loop)
        self.loop_thread.start()

        return self

    def stop(self) -> 'SwimClient':
        """
        Stop the client.
        Schedule a task for stopping the event loop and its thread and afterwards close the loop.
        """
        self.schedule_task(self.__stop_event_loop)
        self.loop_thread.join()
        self.loop.close()

        return self

    def command(self, host_uri: str, node_uri: str, lane_uri: str, body: 'Item') -> None:
        """
        Send a command message to a command lane on a remote Swim agent.

        :param host_uri:        - Host URI of the remote agent.
        :param node_uri:        - Node URI of the remote agent.
        :param lane_uri:        - Lane URI of the command lane of the remote agent.
        :param body:            - The message body.
        """
        host_uri = URI.normalise_warp_scheme(host_uri)
        message = CommandMessage(node_uri, lane_uri, body=body)
        self.schedule_task(self.__send_command, host_uri, message)

    def downlink_value(self) -> 'ValueDownlinkView':
        """
        Create a Value Downlink.
        """
        return ValueDownlinkView(self)

    async def add_downlink_view(self, downlink_view: 'ValueDownlinkView') -> None:
        """
        Add a DownlinkView to the connection pool of the client.

        :param downlink_view:   - DownlinkView to add to the connection pool.
        """
        await self.__connection_pool.add_downlink_view(downlink_view)

    async def remove_downlink_view(self, downlink_view: 'ValueDownlinkView') -> None:
        """
        Remove a DownlinkView from the connection pool of the client.

        :param downlink_view:   - DownlinkView to remove from the connection pool.
        """
        await self.__connection_pool.remove_downlink_view(downlink_view)

    async def get_connection(self, host_uri: str) -> 'WSConnection':
        """
        Get a WebSocket connection to the specified host from the connection pool.

        :param host_uri:        - URI of the host.
        :return:                - WebSocket connection to the host.
        """
        connection = await self.__connection_pool.get_connection(host_uri)
        return connection

    def schedule_task(self, task: Callable, *args: Any) -> 'Future':
        """
        Schedule a task for execution in the asyncio loop.

        :param task:            - Coroutine or function to be executed in the asyncio loop.
        :param args:            - Arguments to be passed to the coroutine or function.
        :return:                - Future object that holds information about the task execution and final result.
        """
        try:
            if inspect.iscoroutinefunction(task):
                future = asyncio.run_coroutine_threadsafe(task(*args), loop=self.loop)
            else:
                future = self.loop.run_in_executor(self.__get_pool_executor(), task, *args)

            future.add_done_callback(self.__exception_handler)
            return future

        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.__handle_exception(exc_value, exc_traceback)

    def __exception_handler(self, future: Future) -> None:
        """
        Check the result of execution of a future and report any exceptions.

        :param future:          - Future that has been completed.
        """
        try:
            future.result()
        except CancelledError:
            pass
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.__handle_exception(exc_value, exc_traceback)

    def __handle_exception(self, exc_value: Optional[Exception], exc_traceback: Optional[TracebackException]) -> None:
        """
        Report exceptions and schedule custom callbacks or client termination, based on the
        Swim Client policies.

        :param exc_value:       - Exception value.
        :param exc_traceback:   - Exception traceback.
        """
        print(exc_value)
        traceback.print_tb(exc_traceback)

        if self.terminate_on_exception:
            os._exit(1)

        if self.execute_on_exception:
            self.schedule_task(self.execute_on_exception)

    async def __send_command(self, host_uri: str, message: 'Envelope') -> None:
        """
        Send a command message to a given host.

        :param host_uri:        - URI of the host.
        :param message:         - Message to send to the host.
        """
        connection = await self.get_connection(host_uri)
        await connection.send_message(await message.to_recon())

    def __get_pool_executor(self) -> 'ThreadPoolExecutor':
        """
        Return the singleton Thread pool executor or create one if it does not exist.

        :return:                - Thread pool executor.
        """
        if self.executor is None:
            self.executor = ThreadPoolExecutor()

        return self.executor

    def __start_event_loop(self) -> None:
        asyncio.set_event_loop(self.loop)
        asyncio.get_event_loop().run_forever()

    async def __stop_event_loop(self) -> None:

        if self.executor is not None:
            self.executor.shutdown(wait=False)

        tasks = [task for task in asyncio.all_tasks(self.loop) if task is not asyncio.current_task(self.loop)]
        [task.cancel() for task in tasks]
        await asyncio.gather(*tasks, return_exceptions=True)

        self.loop.stop()
