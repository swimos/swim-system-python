import unittest
from unittest.mock import patch
from aiounittest import async_test

from swimai.client import WSConnection, ConnectionStatus, ConnectionPool
from test.utils import AsyncMock, MockWebsocket


class TestWsConnections(unittest.TestCase):

    def setUp(self):
        MockWebsocket.clear()

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

    @patch('websockets.connect', new_callable=AsyncMock)
    @async_test
    async def test_ws_connection_subscribe_single(self, mock_websocket):
        # Given
        host_uri = 'ws://localhost:9001'
        actual = WSConnection(host_uri)
        # When
        await actual.subscribe()
        # Then
        self.assertEqual(host_uri, actual.host_uri)
        self.assertEqual(MockWebsocket.get_mock_websocket(), actual.websocket)
        self.assertEqual(ConnectionStatus.OPEN, actual.status)
        self.assertTrue(actual.has_subscribers())
        mock_websocket.assert_called_once_with('ws://localhost:9001')

    @patch('websockets.connect', new_callable=AsyncMock)
    @async_test
    async def test_ws_connection_subscribe_multiple(self, mock_websocket):
        # Given
        host_uri = 'ws://1.1.1.1:9001'
        actual = WSConnection(host_uri)
        # When
        await actual.subscribe()
        await actual.subscribe()
        # Then
        self.assertEqual(host_uri, actual.host_uri)
        self.assertEqual(MockWebsocket.get_mock_websocket(), actual.websocket)
        self.assertEqual(ConnectionStatus.OPEN, actual.status)
        self.assertTrue(actual.has_subscribers())
        mock_websocket.assert_called_once_with('ws://1.1.1.1:9001')

    @async_test
    async def test_ws_connection_subscribe_invalid_uri(self):
        # Given
        host_uri = 'foo_bar'
        actual = WSConnection(host_uri)
        # When
        with self.assertRaises(Exception) as error:
            await actual.subscribe()
        # Then
        message = error.exception.args[0]
        self.assertEqual('foo_bar isn\'t a valid URI', message)

    @patch('websockets.connect', new_callable=AsyncMock)
    @async_test
    async def test_ws_connection_unsubscribe_all(self, mock_websocket):
        # Given
        host_uri = 'ws://0.0.0.0:9001'
        actual = WSConnection(host_uri)
        await actual.subscribe()
        # When
        await actual.unsubscribe()
        # Then
        self.assertEqual(host_uri, actual.host_uri)
        self.assertEqual(MockWebsocket.get_mock_websocket(), actual.websocket)
        self.assertEqual(ConnectionStatus.CLOSED, actual.status)
        self.assertFalse(actual.has_subscribers())
        mock_websocket.assert_called_once_with('ws://0.0.0.0:9001')
        self.assertTrue(actual.websocket.closed)

    @patch('websockets.connect', new_callable=AsyncMock)
    @async_test
    async def test_ws_connection_unsubscribe_one(self, mock_websocket):
        # Given
        host_uri = 'ws://1.2.3.4:9001'
        actual = WSConnection(host_uri)
        await actual.subscribe()
        await actual.subscribe()
        # When
        await actual.unsubscribe()
        # Then
        self.assertEqual(host_uri, actual.host_uri)
        self.assertEqual(MockWebsocket.get_mock_websocket(), actual.websocket)
        self.assertEqual(ConnectionStatus.OPEN, actual.status)
        self.assertTrue(actual.has_subscribers())
        mock_websocket.assert_called_once_with('ws://1.2.3.4:9001')
        self.assertFalse(actual.websocket.closed)

    @patch('websockets.connect', new_callable=AsyncMock)
    @async_test
    async def test_connection_pool_get_connection_new(self, mock_websocket):
        # Given
        host_uri = 'ws://4.3.2.1:9001'
        pool = ConnectionPool()
        # When
        actual = await pool.get_connection(host_uri)
        # Then
        self.assertFalse(actual.closed)
        self.assertEqual(MockWebsocket.get_mock_websocket(), actual)
        self.assertEqual(1, pool.size)
        mock_websocket.assert_called_once_with('ws://4.3.2.1:9001')

    @patch('websockets.connect', new_callable=AsyncMock)
    @async_test
    async def test_connection_pool_get_connection_existing(self, mock_websocket):
        # Given
        host_uri = 'ws://2.2.2.2:9001'
        pool = ConnectionPool()
        await pool.get_connection(host_uri)
        # When
        actual = await pool.get_connection(host_uri)
        # Then
        self.assertFalse(actual.closed)
        self.assertEqual(MockWebsocket.get_mock_websocket(), actual)
        self.assertEqual(1, pool.size)
        mock_websocket.assert_called_once_with('ws://2.2.2.2:9001')

    @patch('websockets.connect', new_callable=AsyncMock)
    @async_test
    async def test_connection_pool_get_connection_multiple(self, mock_websocket):
        # Given
        second_host_uri = 'ws://2.2.2.2:9001'
        first_host_uri = 'ws://1.1.1.1:9001'
        pool = ConnectionPool()
        await pool.get_connection(first_host_uri)
        # When
        actual = await pool.get_connection(second_host_uri)
        # Then
        self.assertFalse(actual.closed)
        self.assertEqual(MockWebsocket.get_mock_websocket(), actual)
        self.assertEqual(2, pool.size)
        mock_websocket.assert_any_call('ws://1.1.1.1:9001')
        mock_websocket.assert_any_call('ws://2.2.2.2:9001')

    @patch('websockets.connect', new_callable=AsyncMock)
    @async_test
    async def test_connection_pool_remove_connection_single_subscriber(self, mock_websocket):
        # Given
        host_uri = 'ws://3.3.3.3:9001'
        pool = ConnectionPool()
        connection = await pool.get_connection(host_uri)
        # When
        await pool.remove_connection(host_uri)
        # Then
        self.assertTrue(connection.closed)
        self.assertEqual(MockWebsocket.get_mock_websocket(), connection)
        self.assertEqual(0, pool.size)
        mock_websocket.assert_called_once_with('ws://3.3.3.3:9001')

    @patch('websockets.connect', new_callable=AsyncMock)
    @async_test
    async def test_connection_pool_remove_connection_multiple_subscribers(self, mock_websocket):
        # Given
        host_uri = 'ws://3.3.3.3:9001'
        pool = ConnectionPool()
        connection = await pool.get_connection(host_uri)
        await pool.get_connection(host_uri)
        # When
        await pool.remove_connection(host_uri)
        # Then
        self.assertFalse(connection.closed)
        self.assertEqual(MockWebsocket.get_mock_websocket(), connection)
        self.assertEqual(1, pool.size)
        mock_websocket.assert_called_once_with('ws://3.3.3.3:9001')

    @async_test
    async def test_connection_pool_remove_connection_non_existing(self):
        # Given
        host_uri = 'foo_bar'
        pool = ConnectionPool()
        # When
        await pool.remove_connection(host_uri)
        # Then
        self.assertEqual(0, pool.size)
