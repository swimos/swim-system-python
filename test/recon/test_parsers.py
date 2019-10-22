import asyncio
import unittest

from aiounittest import async_test

from swim.structures.structs import Num, Text, RecordMap, Attr, Slot
from swim.warp.warp import Envelope, SyncedResponse, CommandMessage, SyncRequest


class TestParser(unittest.TestCase):

    @async_test
    async def test_parse_sync(self):
        # Given
        message = '@sync(node: foo, lane: bar)'
        expected = SyncRequest('foo', 'bar')
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual(expected.tag, actual.tag)
        self.assertEqual(expected.node_uri, actual.node_uri)
        self.assertEqual(expected.lane_uri, actual.lane_uri)

    @async_test
    async def test_parse_sync_escaped(self):
        # Given
        message = '@sync(node: "bar/baz/2", lane: "foo/bar")'
        expected = SyncRequest('bar/baz/2', 'foo/bar')
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual(expected.tag, actual.tag)
        self.assertEqual(expected.node_uri, actual.node_uri)
        self.assertEqual(expected.lane_uri, actual.lane_uri)

    @async_test
    async def test_parse_sync_body_int(self):
        # Given
        message = '@sync(node: "bar/baz/2", lane: "foo/bar")43'
        expected = SyncRequest('bar/baz/2', 'foo/bar', body=Num.create_from(43))
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual(expected.tag, actual.tag)
        self.assertEqual(expected.node_uri, actual.node_uri)
        self.assertEqual(expected.lane_uri, actual.lane_uri)
        self.assertEqual(expected.body.value, actual.body.value)

    @async_test
    async def test_parse_sync_body_float(self):
        # Given
        message = '@sync(node: "bar/baz/2", lane: "foo/bar")0.31'
        expected = SyncRequest('bar/baz/2', 'foo/bar', body=Num.create_from(0.31))
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual(expected.tag, actual.tag)
        self.assertEqual(expected.node_uri, actual.node_uri)
        self.assertEqual(expected.lane_uri, actual.lane_uri)
        self.assertEqual(expected.body.value, actual.body.value)

    @async_test
    async def test_parse_sync_body_string(self):
        # Given
        message = '@sync(node: "bar/baz/2", lane: "foo/bar")"Hello, World"'
        expected = SyncRequest('bar/baz/2', 'foo/bar', body=Text.create_from('Hello, World'))
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual(expected.tag, actual.tag)
        self.assertEqual(expected.node_uri, actual.node_uri)
        self.assertEqual(expected.lane_uri, actual.lane_uri)
        self.assertEqual(expected.body.value, actual.body.value)

    @async_test
    async def test_parse_sync_prio(self):
        # Given
        message = '@sync(node: foo, lane: bar, prio: 3.2)'
        expected = SyncRequest('foo', 'bar', prio=3.2)
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual(expected.node_uri, actual.node_uri)
        self.assertEqual(expected.lane_uri, actual.lane_uri)
        self.assertEqual(expected.prio, actual.prio)

    @async_test
    async def test_parse_sync_rate(self):
        # Given
        message = '@sync(node: foo, lane: bar, rate: 33)'
        expected = SyncRequest('foo', 'bar', rate=33)
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual(expected.node_uri, actual.node_uri)
        self.assertEqual(expected.lane_uri, actual.lane_uri)
        self.assertEqual(expected.rate, actual.rate)

    @async_test
    async def test_parse_sync_prio_rate(self):
        # Given
        message = '@sync(node: foo, lane: bar, prio: 13, rate: 37)'
        expected = SyncRequest('foo', 'bar', prio=13, rate=37)
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual(expected.node_uri, actual.node_uri)
        self.assertEqual(expected.lane_uri, actual.lane_uri)
        self.assertEqual(expected.prio, actual.prio)
        self.assertEqual(expected.rate, actual.rate)

    @async_test
    async def test_parse_synced(self):
        # Given
        message = '@synced(node: foo, lane: bar)'
        expected = SyncedResponse('foo', 'bar')
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual(expected.tag, actual.tag)
        self.assertEqual(expected.node_uri, actual.node_uri)
        self.assertEqual(expected.lane_uri, actual.lane_uri)

    @async_test
    async def test_parse_synced_escaped(self):
        # Given
        message = '@synced(node: "foo/bar", lane: "lane/uri/test")'
        expected = SyncedResponse('foo/bar', 'lane/uri/test')
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual(expected.tag, actual.tag)
        self.assertEqual(expected.node_uri, actual.node_uri)
        self.assertEqual(expected.lane_uri, actual.lane_uri)

    @async_test
    async def test_parse_synced_body_int(self):
        # Given
        message = '@synced(node: foo, lane: bar)33'
        expected = SyncedResponse('foo', 'bar', body=Num.create_from(33))
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual(expected.tag, actual.tag)
        self.assertEqual(expected.node_uri, actual.node_uri)
        self.assertEqual(expected.lane_uri, actual.lane_uri)
        self.assertEqual(expected.body.value, actual.body.value)

    @async_test
    async def test_parse_synced_body_float(self):
        # Given
        message = '@synced(node: foo, lane: bar)37.13'
        expected = SyncedResponse('foo', 'bar', body=Num.create_from(37.13))
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual(expected.tag, actual.tag)
        self.assertEqual(expected.node_uri, actual.node_uri)
        self.assertEqual(expected.lane_uri, actual.lane_uri)
        self.assertEqual(expected.body.value, actual.body.value)

    @async_test
    async def test_parse_synced_body_string(self):
        # Given
        message = '@synced(node: foo, lane: bar)"Hello, World"'
        expected = SyncedResponse('foo', 'bar', body=Text.create_from('Hello, World'))
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual(expected.tag, actual.tag)
        self.assertEqual(expected.node_uri, actual.node_uri)
        self.assertEqual(expected.lane_uri, actual.lane_uri)
        self.assertEqual(expected.body.value, actual.body.value)

    @async_test
    async def test_parse_command(self):
        # Given
        message = '@command(node: foo, lane: bar)'
        expected = CommandMessage('foo', 'bar')
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual(expected.tag, actual.tag)
        self.assertEqual(expected.node_uri, actual.node_uri)
        self.assertEqual(expected.lane_uri, actual.lane_uri)

    @async_test
    async def test_parse_command_escaped(self):
        # Given
        message = '@command(node: "foo/bar", lane: "lane/uri/test")'
        expected = CommandMessage('foo/bar', 'lane/uri/test')
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual(expected.tag, actual.tag)
        self.assertEqual(expected.node_uri, actual.node_uri)
        self.assertEqual(expected.lane_uri, actual.lane_uri)

    @async_test
    async def test_parse_command_body_int(self):
        # Given
        message = '@command(node: "foo/bar", lane: "lane/uri/test")-24'
        expected = CommandMessage('foo/bar', 'lane/uri/test', Num.create_from(-24))
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual(expected.tag, actual.tag)
        self.assertEqual(expected.node_uri, actual.node_uri)
        self.assertEqual(expected.lane_uri, actual.lane_uri)
        self.assertEqual(expected.body.value, actual.body.value)

    @async_test
    async def test_parse_command_body_float(self):
        # Given
        message = '@command(node: "foo/bar", lane: "lane/uri/test")-0.5'
        expected = CommandMessage('foo/bar', 'lane/uri/test', Num.create_from(-0.5))
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual(expected.tag, actual.tag)
        self.assertEqual(expected.node_uri, actual.node_uri)
        self.assertEqual(expected.lane_uri, actual.lane_uri)
        self.assertEqual(expected.body.value, actual.body.value)

    @async_test
    async def test_parse_command_body_string(self):
        # Given
        message = '@command(node: "foo/bar", lane: "lane/uri/test")"0.32"'
        expected = CommandMessage('foo/bar', 'lane/uri/test', Text.create_from('0.32'))
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual(expected.tag, actual.tag)
        self.assertEqual(expected.node_uri, actual.node_uri)
        self.assertEqual(expected.lane_uri, actual.lane_uri)
        self.assertEqual(expected.body.value, actual.body.value)

    @async_test
    async def test_parse_command_body_remove(self):
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
