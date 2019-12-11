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
import unittest
from concurrent.futures.thread import ThreadPoolExecutor
from threading import Thread
from unittest.mock import patch
from test.utils import mock_async_callback, mock_sync_callback

from swimai import SwimClient


class TestSwimClient(unittest.TestCase):

    def test_swim_client_start(self):
        # Given
        client = SwimClient()
        # When
        actual = client.start()
        # Then
        self.assertEqual(actual, client)
        self.assertIsInstance(actual.loop, asyncio.events.AbstractEventLoop)
        self.assertIsInstance(actual.loop_thread, Thread)
        self.assertFalse(actual.loop.is_closed())
        self.assertTrue(actual.loop_thread.is_alive())
        self.assertIsNone(actual.executor)
        client.stop()

    def test_swim_client_stop(self):
        # Given
        client = SwimClient()
        client.start()
        # When
        actual = client.stop()
        # Then
        self.assertEqual(client, actual)
        self.assertIsInstance(actual.loop, asyncio.events.AbstractEventLoop)
        self.assertIsInstance(actual.loop_thread, Thread)
        self.assertTrue(actual.loop.is_closed())
        self.assertFalse(actual.loop_thread.is_alive())
        self.assertIsNone(actual.executor)

    def test_swim_client_with_statement(self):
        # When
        with SwimClient() as swim_client:
            # Then
            self.assertIsInstance(swim_client, SwimClient)
            self.assertIsInstance(swim_client.loop, asyncio.events.AbstractEventLoop)
            self.assertIsInstance(swim_client.loop_thread, Thread)
            self.assertFalse(swim_client.loop.is_closed())

        self.assertIsInstance(swim_client.loop, asyncio.events.AbstractEventLoop)
        self.assertIsInstance(swim_client.loop_thread, Thread)
        self.assertTrue(swim_client.loop.is_closed())
        self.assertFalse(swim_client.loop_thread.is_alive())
        self.assertIsNone(swim_client.executor)

    @patch('builtins.print')
    @patch('traceback.print_tb')
    def test_swim_client_with_statement_exception_no_handler(self, mock_print_tb, mock_print):
        # When
        with SwimClient() as swim_client:
            # Then
            self.assertIsInstance(swim_client, SwimClient)
            self.assertIsInstance(swim_client.loop, asyncio.events.AbstractEventLoop)
            self.assertIsInstance(swim_client.loop_thread, Thread)
            self.assertFalse(swim_client.loop.is_closed())
            self.assertTrue(swim_client.loop_thread.is_alive())

            swim_client.task_with_exception = lambda: (_ for _ in ()).throw(Exception,
                                                                            Exception('Mock exception in task'))

            swim_client.task_with_exception()

        mock_print.assert_called_once()
        mock_print_tb.assert_called_once()
        self.assertEqual('Mock exception in task', mock_print.call_args_list[0][0][0].args[0])
        self.assertTrue(swim_client.loop.is_closed())
        self.assertFalse(swim_client.loop_thread.is_alive())
        self.assertIsNone(swim_client.executor)

    @patch('builtins.print')
    @patch('traceback.print_tb')
    @patch('os._exit')
    def test_swim_client_with_statement_exception_terminate(self, mock_exit, mock_print_tb, mock_print):
        # When
        with SwimClient(terminate_on_exception=True) as swim_client:
            # Then
            self.assertIsInstance(swim_client, SwimClient)
            self.assertIsInstance(swim_client.loop, asyncio.events.AbstractEventLoop)
            self.assertFalse(swim_client.loop.is_closed())
            self.assertIsInstance(swim_client.loop_thread, Thread)
            self.assertTrue(swim_client.loop_thread.is_alive())

            swim_client.task_with_exception = lambda: (_ for _ in ()).throw(Exception,
                                                                            Exception('Mock exception in task'))

            swim_client.task_with_exception()

        self.assertTrue(swim_client.loop.is_closed())
        self.assertEqual('Mock exception in task', mock_print.call_args_list[0][0][0].args[0])
        mock_print_tb.assert_called_once()
        mock_print.assert_called_once()
        mock_exit.assert_called_once_with(1)
        self.assertFalse(swim_client.loop_thread.is_alive())
        self.assertIsNone(swim_client.executor)

    @patch('builtins.print')
    @patch('traceback.print_tb')
    def test_swim_client_with_statement_exception_async_callback(self, mock_print_tb, mock_print):
        # Given
        mock_callback = mock_async_callback
        # When
        with SwimClient(execute_on_exception=mock_callback) as swim_client:
            # Then
            self.assertIsInstance(swim_client.loop, asyncio.events.AbstractEventLoop)
            self.assertIsInstance(swim_client, SwimClient)
            self.assertTrue(swim_client.loop_thread.is_alive())
            self.assertFalse(swim_client.loop.is_closed())
            self.assertIsInstance(swim_client.loop_thread, Thread)

            swim_client.task_with_exception = lambda: (_ for _ in ()).throw(Exception,
                                                                            Exception('Mock exception in task'))

            swim_client.task_with_exception()

        self.assertEqual('Mock exception in task', mock_print.call_args_list[0][0][0].args[0])
        self.assertEqual('Mock async callback', mock_print.call_args_list[1][0][0])
        self.assertEqual(2, mock_print.call_count)
        mock_print_tb.assert_called_once()
        self.assertTrue(swim_client.loop.is_closed())
        self.assertFalse(swim_client.loop_thread.is_alive())
        self.assertIsNone(swim_client.executor)

    @patch('builtins.print')
    @patch('traceback.print_tb')
    def test_swim_client_with_statement_exception_sync_callback(self, mock_print_tb, mock_print):
        # Given
        mock_callback = mock_sync_callback
        # When
        with SwimClient(execute_on_exception=mock_callback) as swim_client:
            # Then
            self.assertIsInstance(swim_client.loop, asyncio.events.AbstractEventLoop)
            self.assertTrue(swim_client.loop_thread.is_alive())
            self.assertIsInstance(swim_client, SwimClient)
            self.assertFalse(swim_client.loop.is_closed())
            self.assertIsInstance(swim_client.loop_thread, Thread)

            swim_client.task_with_exception = lambda: (_ for _ in ()).throw(Exception,
                                                                            Exception('Mock exception in task'))

            swim_client.task_with_exception()

        self.assertEqual('Mock sync callback', mock_print.call_args_list[1][0][0])
        self.assertEqual('Mock exception in task', mock_print.call_args_list[0][0][0].args[0])
        self.assertEqual(2, mock_print.call_count)
        self.assertTrue(swim_client.loop.is_closed())
        mock_print_tb.assert_called_once()
        self.assertFalse(swim_client.loop_thread.is_alive())
        self.assertIsInstance(swim_client.executor, ThreadPoolExecutor)

    @patch('builtins.print')
    @patch('traceback.print_tb')
    @patch('os._exit')
    def test_swim_client_with_statement_exception_callback_and_terminate(self, mock_exit, mock_print_tb, mock_print):
        # Given
        mock_callback = mock_async_callback
        # When
        with SwimClient(terminate_on_exception=True, execute_on_exception=mock_callback) as swim_client:
            # Then
            self.assertIsInstance(swim_client, SwimClient)
            self.assertIsInstance(swim_client.loop, asyncio.events.AbstractEventLoop)
            self.assertFalse(swim_client.loop.is_closed())
            self.assertTrue(swim_client.loop_thread.is_alive())
            self.assertIsInstance(swim_client.loop_thread, Thread)

            swim_client.task_with_exception = lambda: (_ for _ in ()).throw(Exception,
                                                                            Exception('Mock exception in task'))

            swim_client.task_with_exception()

        mock_exit.assert_called_once_with(1)
        self.assertTrue(swim_client.loop.is_closed())
        self.assertEqual('Mock exception in task', mock_print.call_args_list[0][0][0].args[0])
        mock_print_tb.assert_called_once()
        mock_print.assert_called_once()
        self.assertIsNone(swim_client.executor)
        self.assertFalse(swim_client.loop_thread.is_alive())
