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
from swimai.client import WSConnection, ConnectionStatus, ConnectionPool, DownlinkManagerPool, DownlinkManager, \
    DownlinkManagerStatus
from swimai.warp import SyncedResponse
from test.utils import MockWebsocket, MockWebsocketConnect, MockAsyncFunction, MockReceiveMessage, MockConnection, \
    MockDownlink


class TestConnections(unittest.TestCase):
    def setUp(self):
        MockWebsocket.clear()
        MockDownlink.clear()
        MockConnection.clear()

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

    @patch('swimai.client.connections.DownlinkManagerPool.deregister_downlink_view', new_callable=MockAsyncFunction)
    @async_test
    async def test_pool_remove_downlink_view_non_existing_connection(self, mock_deregister_downlink_view):
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
        mock_deregister_downlink_view.assert_not_called()

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
    @patch('swimai.client.connections.DownlinkManager.add_view', new_callable=MockAsyncFunction)
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
    @patch('swimai.client.connections.DownlinkManager.add_view', new_callable=MockAsyncFunction)
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
    @patch('swimai.client.connections.DownlinkManager.add_view', new_callable=MockAsyncFunction)
    @patch('swimai.client.connections.DownlinkManager.remove_view', new_callable=MockAsyncFunction)
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
    @patch('swimai.client.connections.DownlinkManager.add_view', new_callable=MockAsyncFunction)
    @patch('swimai.client.connections.DownlinkManager.remove_view', new_callable=MockAsyncFunction)
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
    @patch('swimai.client.connections.DownlinkManager.add_view', new_callable=MockAsyncFunction)
    @patch('swimai.client.connections.DownlinkManager.receive_message', new_callable=MockAsyncFunction)
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

    @patch('websockets.connect', new_callable=MockWebsocketConnect)
    @patch('swimai.client.connections.DownlinkManager.add_view', new_callable=MockAsyncFunction)
    @patch('swimai.client.connections.DownlinkManager.receive_message', new_callable=MockReceiveMessage)
    @async_test
    async def test_ws_connection_wait_for_message_receive_multiple(self, mock_receive_message, mock_add_view,
                                                                   mock_websocket):
        # Given
        host_uri = 'ws://2.2.2.2:9001'
        connection = WSConnection(host_uri)
        MockWebsocket.get_mock_websocket().connection = connection
        mock_receive_message.set_call_count(3)

        client = SwimClient()
        downlink_view = client.downlink_value()
        downlink_view.set_host_uri(host_uri)
        downlink_view.set_node_uri('baz')
        downlink_view.set_lane_uri('qux')
        await connection.subscribe(downlink_view)

        first_message = '@synced(node:baz,lane:qux)'
        second_message = '@linked(node:baz,lane:qux)'
        third_message = '@synced(node:baz,lane:qux)'

        expected = {first_message, second_message, third_message}
        connection.websocket.messages_to_send.append(first_message)
        connection.websocket.messages_to_send.append(second_message)
        connection.websocket.messages_to_send.append(third_message)
        # When
        await connection.wait_for_messages()
        await mock_receive_message.all_messages_has_been_sent().wait()
        # Then
        messages = mock_receive_message.call_args_list
        first_actual_message = (await asyncio.gather(messages[0][0][0].to_recon()))[0]
        second_actual_message = (await asyncio.gather(messages[1][0][0].to_recon()))[0]
        third_actual_message = (await asyncio.gather(messages[2][0][0].to_recon()))[0]
        actual = {first_actual_message, second_actual_message, third_actual_message}
        self.assertEqual(expected, actual)
        self.assertEqual(ConnectionStatus.CLOSED, connection.status)
        mock_add_view.assert_called_once_with(downlink_view)
        mock_websocket.assert_called_once_with(host_uri)
        self.assertEqual(3, mock_receive_message.call_count)

    @patch('websockets.connect', new_callable=MockWebsocketConnect)
    @patch('swimai.client.connections.DownlinkManager.add_view', new_callable=MockAsyncFunction)
    @patch('swimai.client.connections.DownlinkManager.receive_message', new_callable=MockReceiveMessage)
    @async_test
    async def test_ws_connection_wait_for_message_receive_exception(self, mock_receive_message, mock_add_view,
                                                                    mock_websocket):
        # Given
        host_uri = 'ws://5.5.5.5:9001'
        connection = WSConnection(host_uri)
        MockWebsocket.get_mock_websocket().connection = connection
        mock_websocket.set_raise_exception(True)

        client = SwimClient()
        downlink_view = client.downlink_value()
        downlink_view.set_host_uri(host_uri)
        downlink_view.set_node_uri('boo')
        downlink_view.set_lane_uri('far')
        await connection.subscribe(downlink_view)
        # When
        with self.assertRaises(Exception) as error:
            await connection.wait_for_messages()
        # Then
        message = error.exception.args[0]
        self.assertEqual('WebSocket Exception!', message)
        mock_receive_message.assert_not_called()
        mock_websocket.assert_called_once()
        mock_add_view.assert_called_once_with(downlink_view)

    @async_test
    async def test_downlink_manager_pool(self):
        # When
        actual = DownlinkManagerPool()
        # Then
        self.assertIsInstance(actual, DownlinkManagerPool)
        self.assertEqual(0, actual.size)

    @patch('swimai.client.connections.DownlinkManager.open', new_callable=MockAsyncFunction)
    @async_test
    async def test_downlink_manager_pool_register_downlink_view_single(self, mock_open):
        # Given
        client = SwimClient()
        downlink_view = client.downlink_value()
        downlink_view.set_node_uri('boo')
        downlink_view.set_lane_uri('far')
        actual = DownlinkManagerPool()
        # When
        await actual.register_downlink_view(downlink_view)
        # Then
        self.assertEqual(1, actual.size)
        mock_open.assert_called_once()

    @patch('swimai.client.connections.DownlinkManager.open', new_callable=MockAsyncFunction)
    @async_test
    async def test_downlink_manager_pool_register_downlink_view_multiple_different_routes(self, mock_open):
        # Given
        client = SwimClient()
        first_downlink_view = client.downlink_value()
        first_downlink_view.set_node_uri('boo')
        first_downlink_view.set_lane_uri('far')
        second_downlink_view = client.downlink_value()
        second_downlink_view.set_node_uri('poo')
        second_downlink_view.set_lane_uri('par')
        actual = DownlinkManagerPool()
        # When
        await actual.register_downlink_view(first_downlink_view)
        await actual.register_downlink_view(second_downlink_view)
        # Then
        self.assertEqual(2, actual.size)
        self.assertEqual(2, mock_open.call_count)

    @patch('swimai.client.connections.DownlinkManager.open', new_callable=MockAsyncFunction)
    @async_test
    async def test_downlink_manager_pool_register_downlink_view_multiple_same_route(self, mock_open):
        # Given
        client = SwimClient()
        first_downlink_view = client.downlink_value()
        first_downlink_view.set_node_uri('boo')
        first_downlink_view.set_lane_uri('far')
        second_downlink_view = client.downlink_value()
        second_downlink_view.set_node_uri('boo')
        second_downlink_view.set_lane_uri('far')
        actual = DownlinkManagerPool()
        # When
        await actual.register_downlink_view(first_downlink_view)
        await actual.register_downlink_view(second_downlink_view)
        # Then
        self.assertEqual(1, actual.size)
        mock_open.assert_called_once()

    @patch('swimai.client.connections.DownlinkManager.close', new_callable=MockAsyncFunction)
    @patch('swimai.client.connections.DownlinkManager.open', new_callable=MockAsyncFunction)
    @async_test
    async def test_downlink_manager_pool_deregister_downlink_view_single_existing(self, mock_open, mock_close):
        # Given
        client = SwimClient()
        downlink_view = client.downlink_value()
        downlink_view.set_node_uri('moo')
        downlink_view.set_lane_uri('cow')
        actual = DownlinkManagerPool()
        await actual.register_downlink_view(downlink_view)
        # When
        await actual.deregister_downlink_view(downlink_view)
        # Then
        self.assertEqual(0, actual.size)
        mock_open.assert_called_once()
        mock_close.assert_called_once()

    @patch('swimai.client.connections.DownlinkManager.close', new_callable=MockAsyncFunction)
    @async_test
    async def test_downlink_manager_pool_deregister_downlink_view_single_non_existing(self, mock_close):
        # Given
        client = SwimClient()
        downlink_view = client.downlink_value()
        downlink_view.set_node_uri('foo')
        downlink_view.set_lane_uri('bar')
        actual = DownlinkManagerPool()
        # When
        await actual.deregister_downlink_view(downlink_view)
        # Then
        self.assertEqual(0, actual.size)
        mock_close.assert_not_called()

    @patch('swimai.client.connections.DownlinkManager.close', new_callable=MockAsyncFunction)
    @patch('swimai.client.connections.DownlinkManager.open', new_callable=MockAsyncFunction)
    @async_test
    async def test_downlink_manager_pool_deregister_downlink_view_multiple_same_route(self, mock_open, mock_close):
        # Given
        client = SwimClient()
        first_downlink_view = client.downlink_value()
        first_downlink_view.set_node_uri('qux')
        first_downlink_view.set_lane_uri('baz')
        second_downlink_view = client.downlink_value()
        second_downlink_view.set_node_uri('qux')
        second_downlink_view.set_lane_uri('baz')
        actual = DownlinkManagerPool()
        await actual.register_downlink_view(first_downlink_view)
        await actual.register_downlink_view(second_downlink_view)
        # When
        await actual.deregister_downlink_view(first_downlink_view)
        await actual.deregister_downlink_view(second_downlink_view)
        # Then
        self.assertEqual(0, actual.size)
        self.assertEqual(1, mock_open.call_count)
        self.assertEqual(1, mock_close.call_count)

    @patch('swimai.client.connections.DownlinkManager.close', new_callable=MockAsyncFunction)
    @patch('swimai.client.connections.DownlinkManager.open', new_callable=MockAsyncFunction)
    @async_test
    async def test_downlink_manager_pool_deregister_downlink_view_multiple_different_routes(self, mock_open,
                                                                                            mock_close):
        # Given
        client = SwimClient()
        first_downlink_view = client.downlink_value()
        first_downlink_view.set_node_uri('parrot')
        first_downlink_view.set_lane_uri('dead')
        second_downlink_view = client.downlink_value()
        second_downlink_view.set_node_uri('ghost')
        second_downlink_view.set_lane_uri('boo')
        actual = DownlinkManagerPool()
        await actual.register_downlink_view(first_downlink_view)
        await actual.register_downlink_view(second_downlink_view)
        # When
        await actual.deregister_downlink_view(first_downlink_view)
        await actual.deregister_downlink_view(second_downlink_view)
        # Then
        self.assertEqual(0, actual.size)
        self.assertEqual(2, mock_open.call_count)
        self.assertEqual(2, mock_close.call_count)

    @patch('swimai.client.connections.DownlinkManager.open', new_callable=MockAsyncFunction)
    @patch('swimai.client.connections.DownlinkManager.receive_message', new_callable=MockAsyncFunction)
    @async_test
    async def test_downlink_manager_pool_receive_message_existing_route(self, mock_receive_message, mock_open):
        # Given
        client = SwimClient()
        downlink_view = client.downlink_value()
        downlink_view.set_node_uri('moo')
        downlink_view.set_lane_uri('cow')
        actual = DownlinkManagerPool()
        await actual.register_downlink_view(downlink_view)
        message = SyncedResponse('moo', 'cow')
        # When
        await actual.receive_message(message)
        # Then
        mock_open.assert_called_once()
        mock_receive_message.assert_called_once_with(message)

    @patch('swimai.client.connections.DownlinkManager.open', new_callable=MockAsyncFunction)
    @patch('swimai.client.connections.DownlinkManager.receive_message', new_callable=MockAsyncFunction)
    @async_test
    async def test_downlink_manager_pool_receive_message_non_existing_route(self, mock_receive_message, mock_open):
        # Given
        client = SwimClient()
        downlink_view = client.downlink_value()
        downlink_view.set_node_uri('moo')
        downlink_view.set_lane_uri('cow')
        actual = DownlinkManagerPool()
        await actual.register_downlink_view(downlink_view)
        message = SyncedResponse('poo', 'pow')
        # When
        await actual.receive_message(message)
        # Then
        mock_open.assert_called_once()
        mock_receive_message.assert_not_called()

    @async_test
    async def test_downlink_manager(self):
        # Given
        host_uri = 'ws://5.5.5.5:9001'
        connection = WSConnection(host_uri)
        # When
        actual = DownlinkManager(connection)
        # Then
        self.assertIsInstance(actual, DownlinkManager)
        self.assertIsNone(actual.downlink_model)
        self.assertEqual(connection, actual.connection)
        self.assertEqual(0, actual.view_count)
        self.assertEqual(DownlinkManagerStatus.CLOSED, actual.status)

    @patch('swimai.client.swim_client.SwimClient.schedule_task')
    @async_test
    async def test_downlink_manager_open_new(self, mock_schedule_task):
        # Given
        host_uri = 'ws://5.5.5.5:9001'
        connection = WSConnection(host_uri)
        client = SwimClient()
        downlink_view = client.downlink_value()
        downlink_view.set_node_uri('foo')
        downlink_view.set_lane_uri('bar')
        downlink_model = await downlink_view.create_downlink_model()
        downlink_model.connection = MockConnection.get_mock_connection()
        actual = DownlinkManager(connection)
        actual.downlink_model = downlink_model
        # When
        await actual.open()
        # Then
        self.assertEqual(DownlinkManagerStatus.OPEN, actual.status)
        mock_schedule_task.assert_called_once_with(MockConnection.get_mock_connection().wait_for_messages)
        self.assertEqual(1, len(MockConnection.get_mock_connection().messages_sent))
        self.assertEqual('@sync(node:foo,lane:bar)', MockConnection.get_mock_connection().messages_sent[0])

    @patch('swimai.client.swim_client.SwimClient.schedule_task')
    @async_test
    async def test_downlink_manager_open_existing(self, mock_schedule_task):
        # Given
        host_uri = 'ws://5.5.5.5:9001'
        connection = WSConnection(host_uri)
        client = SwimClient()
        downlink_view = client.downlink_value()
        downlink_view.set_node_uri('moo')
        downlink_view.set_lane_uri('car')
        downlink_model = await downlink_view.create_downlink_model()
        actual = DownlinkManager(connection)
        downlink_model.connection = MockConnection.get_mock_connection()
        actual.downlink_model = downlink_model
        await actual.open()
        # When
        await actual.open()
        # Then
        self.assertEqual(DownlinkManagerStatus.OPEN, actual.status)
        self.assertEqual('@sync(node:moo,lane:car)', MockConnection.get_mock_connection().messages_sent[0])
        self.assertEqual(1, len(MockConnection.get_mock_connection().messages_sent))
        mock_schedule_task.assert_called_once_with(MockConnection.get_mock_connection().wait_for_messages)
