import asyncio
import unittest

from aiounittest import async_test

from swim.structures.structs import Num, Text, RecordMap, Attr, Slot
from swim.warp.warp import Envelope, SyncedResponse


class TestParser(unittest.TestCase):

    @async_test
    async def test_parse_synced_escaped(self):
        # Given
        message = '@synced(node: "foo/bar", lane: "lane/uri/test")'
        expected = SyncedResponse('foo/bar', 'lane/uri/test')
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual(expected.node_uri, actual.node_uri)
        self.assertEqual(expected.lane_uri, actual.lane_uri)

    @async_test
    async def test_parse_synced(self):
        # Given
        message = '@synced(node: foo, lane: bar)'
        expected = SyncedResponse('foo', 'bar')
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual(expected.node_uri, actual.node_uri)
        self.assertEqual(expected.lane_uri, actual.lane_uri)

    @async_test
    async def test_parse_synced_body_int(self):
        # Given
        message = '@synced(node: foo, lane: bar) 33'
        expected = SyncedResponse('foo', 'bar', body=Num.create_from(33))
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual(expected.node_uri, actual.node_uri)
        self.assertEqual(expected.lane_uri, actual.lane_uri)
        self.assertEqual(expected.body.value, actual.body.value)

    @async_test
    async def test_parse_synced_body_float(self):
        # Given
        message = '@synced(node: foo, lane: bar) 37.13'
        expected = SyncedResponse('foo', 'bar', body=Num.create_from(37.13))
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual(expected.node_uri, actual.node_uri)
        self.assertEqual(expected.lane_uri, actual.lane_uri)
        self.assertEqual(expected.body.value, actual.body.value)

    @async_test
    async def test_parse_synced_body_string(self):
        # Given
        message = '@synced(node: foo, lane: bar) "Hello, World"'
        expected = SyncedResponse('foo', 'bar', body=Text.create_from('Hello, World'))
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual(expected.node_uri, actual.node_uri)
        self.assertEqual(expected.lane_uri, actual.lane_uri)
        self.assertEqual(expected.body.value, actual.body.value)

    @async_test
    async def test_parse_command_remove_key(self):
        # Given
        message = '@command(node:"/unit/foo",lane:shoppingCart)@remove(key:FromClientLink)'
        expected = SyncedResponse('/unit/foo', 'shoppingCart',
                                  body=RecordMap.of(
                                      Attr.of(Text.create_from('remove'),
                                              RecordMap.of(Slot.of(Text.create_from('key'), Text.create_from('FromClientLink'))))))

        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual(expected.node_uri, actual.node_uri)
        self.assertEqual(expected.lane_uri, actual.lane_uri)
        self.assertEqual(expected.body.items[0].key.value, actual.body.items[0].key.value)
        self.assertEqual(expected.body.items[0].value.items[0].key.value, actual.body.items[0].value.items[0].key.value)
        self.assertEqual(expected.body.items[0].value.items[0].value.value, actual.body.items[0].value.items[0].value.value)
