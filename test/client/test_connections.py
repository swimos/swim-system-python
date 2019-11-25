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

from unittest.mock import patch
from aiounittest import async_test
from swimai import SwimClient
from swimai.client import WSConnection, ConnectionStatus, ConnectionPool
from test.utils import MockWebsocket, MockWebsocketConnect, MockAsyncFunction


class TestConnections(unittest.TestCase):
    def setUp(self):
        MockWebsocket.clear()

    def test_connection_pool(self):
        # When
        actual = ConnectionPool()
        # Then
        self.assertEqual(0, actual.size)

    @async_test
    async def test_pool_get_connection_new(self):
        # Given
        pool = ConnectionPool()
        uri = 'ws://foo_bar:9000'
        # When
        actual = await pool.get_connection(uri)
        # Then
        self.assertEqual(uri, actual.host_uri)
        self.assertEqual(None, actual.websocket)
        self.assertEqual(ConnectionStatus.CLOSED, actual.status)
        self.assertEqual(1, pool.size)

    @async_test
    async def test_pool_get_connection_existing(self):
        # Given
        pool = ConnectionPool()
        uri = 'ws://foo_bar:9000'
        expected = await pool.get_connection(uri)
        expected.status = ConnectionStatus.IDLE
        # When
        actual = await pool.get_connection(uri)
        # Then
        self.assertEqual(expected, actual)
        self.assertEqual(1, pool.size)

    @async_test
    async def test_pool_get_connection_closed(self):
        # Given
        pool = ConnectionPool()
        uri = 'ws://foo_bar:9000'
        expected = await pool.get_connection(uri)
        # When
        actual = await pool.get_connection(uri)
        # Then
        self.assertNotEqual(expected, actual)
        self.assertEqual(uri, actual.host_uri)
        self.assertEqual(None, actual.websocket)
        self.assertEqual(ConnectionStatus.CLOSED, actual.status)
        self.assertEqual(1, pool.size)

    @async_test
    async def test_pool_remove_connection_existing(self):
        # Given
        pool = ConnectionPool()
        uri = 'ws://foo_bar:9000'
        connection = await pool.get_connection(uri)
        connection.status = ConnectionStatus.IDLE
        # When
        await pool.remove_connection(uri)
        # Then
        self.assertEqual(0, pool.size)
        self.assertEqual(ConnectionStatus.CLOSED, connection.status)

    @async_test
    async def test_pool_remove_connection_non_existing(self):
        # Given
        pool = ConnectionPool()
        uri = 'ws://foo_bar:9000'
        # When
        await pool.remove_connection(uri)
        # Then
        self.assertEqual(0, pool.size)

    @patch('swimai.client.connections.WSConnection.subscribe', new_callable=MockAsyncFunction)
    @async_test
    async def test_pool_add_downlink_view_existing_connection(self, mock_subscribe):
        # Given
        pool = ConnectionPool()
        uri = 'ws://foo_bar:9000'
        connection = await pool.get_connection(uri)
        connection.status = ConnectionStatus.IDLE
        downlink_view = SwimClient().downlink_value()
        downlink_view.set_host_uri(uri)
        # When
        await pool.add_downlink_view(downlink_view)
        # Then
        self.assertEqual(uri, downlink_view.host_uri)
        self.assertEqual(1, pool.size)
        self.assertEqual(uri, connection.host_uri)
        self.assertEqual(connection, downlink_view.connection)
        self.assertEqual(ConnectionStatus.IDLE, connection.status)
        mock_subscribe.assert_called_once_with(downlink_view)

    @patch('swimai.client.connections.WSConnection.subscribe', new_callable=MockAsyncFunction)
    @async_test
    async def test_pool_add_downlink_view_non_existing_connection(self, mock_subscribe):
        # Given
        pool = ConnectionPool()
        uri = 'ws://foo_bar:9000'
        downlink_view = SwimClient().downlink_value()
        downlink_view.set_host_uri(uri)
        # When
        await pool.add_downlink_view(downlink_view)
        # Then
        self.assertEqual(uri, downlink_view.host_uri)
        self.assertEqual(1, pool.size)
        mock_subscribe.assert_called_once_with(downlink_view)

    @patch('swimai.client.connections.WSConnection.subscribe', new_callable=MockAsyncFunction)
    @patch('swimai.client.connections.WSConnection.unsubscribe', new_callable=MockAsyncFunction)
    @async_test
    async def test_pool_remove_downlink_view_existing_connection_open(self, mock_unsubscribe, mock_subscribed):
        # Given
        pool = ConnectionPool()
        uri = 'ws://foo_bar:9000'
        downlink_view = SwimClient().downlink_value()
        downlink_view.set_host_uri(uri)
        await pool.add_downlink_view(downlink_view)
        downlink_view.connection.status = ConnectionStatus.IDLE
        # When
        await pool.remove_downlink_view(downlink_view)
        # Then
        pass
        self.assertEqual(1, pool.size)
        self.assertEqual(ConnectionStatus.IDLE, downlink_view.connection.status)
        mock_subscribed.assert_called_with(downlink_view)
        mock_unsubscribe.assert_called_with(downlink_view)

    @patch('swimai.client.connections.WSConnection.subscribe', new_callable=MockAsyncFunction)
    @patch('swimai.client.connections.WSConnection.unsubscribe', new_callable=MockAsyncFunction)
    @async_test
    async def test_pool_remove_downlink_view_existing_connection_closed(self, mock_unsubscribe, mock_subscribe):
        # Given
        pool = ConnectionPool()
        uri = 'ws://foo_bar:9000'
        downlink_view = SwimClient().downlink_value()
        downlink_view.set_host_uri(uri)
        await pool.add_downlink_view(downlink_view)
        connection = pool.get_connection(uri)
        connection.close()
        # When
        await pool.remove_downlink_view(downlink_view)
        # Then
        pass
        self.assertEqual(0, pool.size)
        self.assertEqual(ConnectionStatus.CLOSED, downlink_view.connection.status)
        mock_subscribe.assert_called_once_with(downlink_view)
        mock_unsubscribe.assert_called_once_with(downlink_view)

    @patch('swimai.client.connections.DownlinkPool.remove_downlink', new_callable=MockAsyncFunction)
    @async_test
    async def test_pool_remove_downlink_view_non_existing_connection(self, mock_remove_downlink):
        # Given
        pool = ConnectionPool()
        uri = 'ws://foo_bar:9000'
        downlink_view = SwimClient().downlink_value()
        downlink_view.set_host_uri(uri)
        await pool.remove_connection(uri)
        # When
        await pool.remove_downlink_view(downlink_view)
        # Then
        pass
        self.assertEqual(0, pool.size)
        mock_remove_downlink.assert_not_called()

    @async_test
    async def test_ws_connection(self):
        # Given
        host_uri = 'ws://localhost:9001'
        # When
        actual = WSConnection(host_uri)
        # Then
        self.assertEqual(host_uri, actual.host_uri)
        self.assertIsNone(actual.websocket)
        self.assertEqual(ConnectionStatus.CLOSED, actual.status)

    @patch('websockets.connect', new_callable=MockWebsocketConnect)
    @patch('swimai.client.connections.Downlink.add_view', new_callable=MockAsyncFunction)
    @async_test
    async def test_ws_connection_subscribe_single(self, mock_add_view, mock_websocket):
        # Given
        host_uri = 'ws://localhost:9001'
        actual = WSConnection(host_uri)
        downlink_view = SwimClient().downlink_value()
        downlink_view.set_host_uri(host_uri)
        downlink_view.set_node_uri('bar')
        downlink_view.set_lane_uri('baz')
        # When
        await actual.subscribe(downlink_view)
        # Then
        self.assertEqual(host_uri, actual.host_uri)
        self.assertEqual(MockWebsocket.get_mock_websocket(), actual.websocket)
        self.assertEqual(ConnectionStatus.IDLE, actual.status)
        self.assertTrue(actual.has_subscribers())
        mock_websocket.assert_called_once_with(host_uri)
        mock_add_view.assert_called_once_with(downlink_view)

    @patch('websockets.connect', new_callable=MockWebsocketConnect)
    @patch('swimai.client.connections.Downlink.add_view', new_callable=MockAsyncFunction)
    @async_test
    async def test_ws_connection_subscribe_multiple(self, mock_add_view, mock_websocket):
        # Given
        host_uri = 'ws://1.1.1.1:9001'
        actual = WSConnection(host_uri)

        client = SwimClient()
        first_downlink_view = client.downlink_value()
        first_downlink_view.set_host_uri(host_uri)
        first_downlink_view.set_node_uri('bar')
        first_downlink_view.set_lane_uri('baz')

        second_downlink_view = client.downlink_value()
        second_downlink_view.set_host_uri(host_uri)
        second_downlink_view.set_node_uri('foo')
        second_downlink_view.set_lane_uri('bar')
        # When
        await actual.subscribe(first_downlink_view)
        await actual.subscribe(second_downlink_view)
        # Then
        self.assertEqual(host_uri, actual.host_uri)
        self.assertEqual(MockWebsocket.get_mock_websocket(), actual.websocket)
        self.assertEqual(ConnectionStatus.IDLE, actual.status)
        self.assertTrue(actual.has_subscribers())
        mock_websocket.assert_called_once_with('ws://1.1.1.1:9001')
        mock_add_view.assert_any_call(first_downlink_view)
        mock_add_view.assert_any_call(second_downlink_view)

    @patch('websockets.connect', new_callable=MockWebsocketConnect)
    @patch('swimai.client.connections.Downlink.add_view', new_callable=MockAsyncFunction)
    @patch('swimai.client.connections.Downlink.remove_view', new_callable=MockAsyncFunction)
    @async_test
    async def test_ws_connection_unsubscribe_all(self, mock_remove_view, mock_add_view, mock_websocket):
        # Given
        host_uri = 'ws://0.0.0.0:9001'
        actual = WSConnection(host_uri)
        downlink_view = SwimClient().downlink_value()
        downlink_view.set_host_uri(host_uri)
        downlink_view.set_node_uri('foo')
        downlink_view.set_lane_uri('bar')

        await actual.subscribe(downlink_view)
        # When
        await actual.unsubscribe(downlink_view)
        # Then
        self.assertEqual(host_uri, actual.host_uri)
        self.assertEqual(MockWebsocket.get_mock_websocket(), actual.websocket)
        self.assertEqual(ConnectionStatus.CLOSED, actual.status)
        self.assertFalse(actual.has_subscribers())
        mock_websocket.assert_called_once_with('ws://0.0.0.0:9001')
        self.assertTrue(actual.websocket.closed)
        mock_add_view.assert_called_once_with(downlink_view)
        mock_remove_view.assert_called_once_with(downlink_view)

    @patch('websockets.connect', new_callable=MockWebsocketConnect)
    @patch('swimai.client.connections.Downlink.add_view', new_callable=MockAsyncFunction)
    @patch('swimai.client.connections.Downlink.remove_view', new_callable=MockAsyncFunction)
    @async_test
    async def test_ws_connection_unsubscribe_one(self, mock_remove_view, mock_add_view, mock_websocket):
        # Given
        host_uri = 'ws://1.2.3.4:9001'
        actual = WSConnection(host_uri)

        client = SwimClient()
        first_downlink_view = client.downlink_value()
        first_downlink_view.set_host_uri(host_uri)
        first_downlink_view.set_node_uri('foo')
        first_downlink_view.set_lane_uri('bar')

        second_downlink_view = client.downlink_value()
        second_downlink_view.set_host_uri(host_uri)
        second_downlink_view.set_node_uri('bar')
        second_downlink_view.set_lane_uri('baz')

        await actual.subscribe(first_downlink_view)
        await actual.subscribe(second_downlink_view)
        # When
        await actual.unsubscribe(first_downlink_view)
        # Then
        self.assertEqual(host_uri, actual.host_uri)
        self.assertEqual(MockWebsocket.get_mock_websocket(), actual.websocket)
        self.assertEqual(ConnectionStatus.IDLE, actual.status)
        self.assertTrue(actual.has_subscribers())
        mock_websocket.assert_called_once_with('ws://1.2.3.4:9001')
        self.assertFalse(actual.websocket.closed)
        mock_add_view.assert_any_call(first_downlink_view)
        mock_add_view.assert_any_call(second_downlink_view)
        mock_remove_view.assert_called_once_with(first_downlink_view)

    @patch('websockets.connect', new_callable=MockWebsocketConnect)
    @async_test
    async def test_ws_connection_open_new(self, mock_websocket):
        # Given
        host_uri = 'ws://1.2.3.4:9001'
        connection = WSConnection(host_uri)
        # When
        await connection.open()
        # Then
        self.assertEqual(ConnectionStatus.IDLE, connection.status)
        mock_websocket.assert_called_once_with(host_uri)

    @patch('websockets.connect', new_callable=MockWebsocketConnect)
    @async_test
    async def test_ws_connection_open_already_opened(self, mock_websocket):
        # Given
        host_uri = 'ws://1.2.3.4:9001'
        connection = WSConnection(host_uri)
        await connection.open()
        # When
        await connection.open()
        # Then
        self.assertEqual(ConnectionStatus.IDLE, connection.status)
        mock_websocket.assert_called_once_with(host_uri)

    @patch('websockets.connect', new_callable=MockWebsocketConnect)
    @async_test
    async def test_ws_connection_close_opened(self, mock_websocket):
        # Given
        host_uri = 'ws://1.2.3.4:9001'
        connection = WSConnection(host_uri)
        await connection.open()
        # When
        await connection.close()
        # Then
        self.assertEqual(ConnectionStatus.CLOSED, connection.status)
        mock_websocket.assert_called_once_with(host_uri)
        self.assertTrue(connection.websocket.closed)

    @patch('websockets.connect', new_callable=MockWebsocketConnect)
    @async_test
    async def test_ws_connection_close_missing_websocket(self, mock_websocket):
        # Given
        host_uri = 'ws://1.2.3.4:9001'
        connection = WSConnection(host_uri)
        # When
        await connection.close()
        # Then
        self.assertEqual(ConnectionStatus.CLOSED, connection.status)
        mock_websocket.assert_not_called()
        self.assertIsNone(connection.websocket)

    @patch('websockets.connect', new_callable=MockWebsocketConnect)
    @async_test
    async def test_ws_connection_close_already_closed(self, mock_websocket):
        # Given
        host_uri = 'ws://5.5.5.5:9001'
        connection = WSConnection(host_uri)
        await connection.open()
        await connection.close()
        # When
        await connection.close()
        # Then
        mock_websocket.assert_called_once_with(host_uri)
        self.assertEqual(ConnectionStatus.CLOSED, connection.status)
        self.assertTrue(connection.websocket.closed)

    @patch('websockets.connect', new_callable=MockWebsocketConnect)
    @async_test
    async def test_ws_connection_send_message_existing_websocket_single(self, mock_websocket):
        # Given
        host_uri = 'ws://1.2.3.4:9001'
        message = 'Hello, World'
        connection = WSConnection(host_uri)
        await connection.open()
        # When
        await connection.send_message(message)
        # Then
        mock_websocket.assert_called_once_with(host_uri)
        self.assertEqual(message, connection.websocket.sent_messages[0])

    @patch('websockets.connect', new_callable=MockWebsocketConnect)
    @async_test
    async def test_ws_connection_send_message_existing_websocket_multiple(self, mock_websocket):
        # Given
        host_uri = 'ws://1.2.3.4:9001'
        first_message = 'Hello, World'
        second_message = 'Hello, Friend'
        connection = WSConnection(host_uri)
        await connection.open()
        # When
        await connection.send_message(first_message)
        await connection.send_message(second_message)
        # Then
        mock_websocket.assert_called_once_with(host_uri)
        self.assertEqual(first_message, connection.websocket.sent_messages[0])
        self.assertEqual(second_message, connection.websocket.sent_messages[1])

    @patch('websockets.connect', new_callable=MockWebsocketConnect)
    @async_test
    async def test_ws_connection_send_message_non_existing_websocket(self, mock_websocket):
        # Given
        host_uri = 'ws://1.2.3.4:9001'
        message = 'Hello, World'
        connection = WSConnection(host_uri)
        # When
        await connection.send_message(message)
        # Then
        mock_websocket.assert_called_once_with(host_uri)
        self.assertEqual(message, connection.websocket.sent_messages[0])

    @patch('websockets.connect', new_callable=MockWebsocketConnect)
    @async_test
    async def test_ws_connection_send_message_closed(self, mock_websocket):
        # Given
        host_uri = 'ws://1.2.3.4:9001'
        message = 'Hello, World'
        connection = WSConnection(host_uri)
        await connection.open()
        await connection.close()
        # When
        await connection.send_message(message)
        # Then
        self.assertEqual(2, mock_websocket.call_count)
        mock_websocket.assert_called_with(host_uri)
        self.assertEqual(message, connection.websocket.sent_messages[0])

    @async_test
    async def test_ws_connection_wait_for_message_closed(self):
        # Given
        host_uri = 'ws://1.2.3.4:9001'
        connection = WSConnection(host_uri)
        # When
        await connection.wait_for_messages()
        # Then
        self.assertEqual(ConnectionStatus.CLOSED, connection.status)

    @patch('websockets.connect', new_callable=MockWebsocketConnect)
    @patch('swimai.client.connections.Downlink.add_view', new_callable=MockAsyncFunction)
    @patch('swimai.client.connections.Downlink.receive_message', new_callable=MockAsyncFunction)
    @async_test
    async def test_ws_connection_wait_for_message_receive_single(self, mock_receive_message, mock_add_view,
                                                                 mock_websocket):
        # Given
        host_uri = 'ws://1.2.3.4:9001'
        connection = WSConnection(host_uri)
        MockWebsocket.get_mock_websocket().connection = connection

        client = SwimClient()
        downlink_view = client.downlink_value()
        downlink_view.set_host_uri(host_uri)
        downlink_view.set_node_uri('foo')
        downlink_view.set_lane_uri('bar')
        await connection.subscribe(downlink_view)

        expected = '@sync(node:foo,lane:bar)'
        connection.websocket.messages_to_send.append(expected)
        # When
        await connection.wait_for_messages()
        # Then
        actual = await asyncio.gather(mock_receive_message.call_args[0][0].to_recon())
        self.assertEqual(expected, actual[0])
        self.assertEqual(ConnectionStatus.CLOSED, connection.status)
        mock_add_view.assert_called_once_with(downlink_view)
        mock_websocket.assert_called_once_with(host_uri)
        mock_receive_message.assert_called_once()

    @async_test
    async def test_ws_connection_wait_for_message_receive_multiple(self):
        # Given
        # When
        # Then
        pass

    @async_test
    async def test_ws_connection_wait_for_message_receive_exception(self):
        # Given
        # When
        # Then
        pass
