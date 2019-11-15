import unittest
from unittest.mock import patch

from aiounittest import async_test

from swimai.client.ws_connections import WSConnection, ConnectionStatus
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
    async def test_ws_subscribe_single(self, mock_websocket):
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
    async def test_ws_subscribe_multiple(self, mock_websocket):
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
    async def test_ws_subscribe_invalid_uri(self):
        # Given
        host_uri = 'foo_bar'
        actual = WSConnection(host_uri)
        # When
        # When
        with self.assertRaises(Exception) as error:
            await actual.subscribe()
        # Then
        message = error.exception.args[0]
        self.assertEqual('foo_bar isn\'t a valid URI', message)

    @patch('websockets.connect', new_callable=AsyncMock)
    @async_test
    async def test_ws_unsubscribe_all(self, mock_websocket):
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
    async def test_ws_unsubscribe_one(self, mock_websocket):
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

    @async_test
    async def test_get_connection_new(self):
        pass

    @async_test
    async def test_get_connection_existing(self):
        pass

    @async_test
    async def test_remove_connection(self):
        pass

    @async_test
    async def test_remove_connection_and_pop(self):
        pass

    @async_test
    async def test_remove_connection_non_existing(self):
        pass
