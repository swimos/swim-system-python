import asyncio
import unittest

from aiounittest import async_test
from swimai.warp.warp import Envelope


class TestParser(unittest.TestCase):

    @async_test
    async def test_parse_sync(self):
        # Given
        message = '@sync(node: foo, lane: bar)'
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual('sync', actual.tag)
        self.assertEqual('foo', actual.node_uri)
        self.assertEqual('bar', actual.lane_uri)

    @async_test
    async def test_parse_sync_escaped(self):
        # Given
        message = '@sync(node: "bar/baz/2", lane: "foo/bar")'
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual('sync', actual.tag)
        self.assertEqual('bar/baz/2', actual.node_uri)
        self.assertEqual('foo/bar', actual.lane_uri)

    @async_test
    async def test_parse_sync_body_int(self):
        # Given
        message = '@sync(node: "bar/baz/2", lane: "foo/bar")43'
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual('sync', actual.tag)
        self.assertEqual('bar/baz/2', actual.node_uri)
        self.assertEqual('foo/bar', actual.lane_uri)
        self.assertEqual(43, actual.body.value)

    @async_test
    async def test_parse_sync_body_float(self):
        # Given
        message = '@sync(node: "bar/baz/2", lane: "foo/bar")0.31'
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual('sync', actual.tag)
        self.assertEqual('bar/baz/2', actual.node_uri)
        self.assertEqual('foo/bar', actual.lane_uri)
        self.assertEqual(0.31, actual.body.value)

    @async_test
    async def test_parse_sync_body_bool(self):
        # Given
        message = '@sync(node: "bar/baz/2", lane: "foo/bar")false'
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual('sync', actual.tag)
        self.assertEqual('bar/baz/2', actual.node_uri)
        self.assertEqual('foo/bar', actual.lane_uri)
        self.assertEqual(False, actual.body.value)

    @async_test
    async def test_parse_sync_body_string(self):
        # Given
        message = '@sync(node: "bar/baz/2", lane: "foo/bar")"Hello, World"'
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual('sync', actual.tag)
        self.assertEqual('bar/baz/2', actual.node_uri)
        self.assertEqual('foo/bar', actual.lane_uri)
        self.assertEqual('Hello, World', actual.body.value)

    @async_test
    async def test_parse_sync_prio(self):
        # Given
        message = '@sync(node: foo, lane: bar, prio: 3.2)'
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual('sync', actual.tag)
        self.assertEqual('foo', actual.node_uri)
        self.assertEqual('bar', actual.lane_uri)
        self.assertEqual(3.2, actual.prio)

    @async_test
    async def test_parse_sync_rate(self):
        # Given
        message = '@sync(node: foo, lane: bar, rate: 33)'
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual('sync', actual.tag)
        self.assertEqual('foo', actual.node_uri)
        self.assertEqual('bar', actual.lane_uri)
        self.assertEqual(33, actual.rate)

    @async_test
    async def test_parse_sync_prio_rate(self):
        # Given
        message = '@sync(node: foo, lane: bar, prio: 13, rate: 37)'
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual('sync', actual.tag)
        self.assertEqual('foo', actual.node_uri)
        self.assertEqual('bar', actual.lane_uri)
        self.assertEqual(13, actual.prio)
        self.assertEqual(37, actual.rate)

    @async_test
    async def test_parse_synced(self):
        # Given
        message = '@synced(node: foo, lane: bar)'
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual('synced', actual.tag)
        self.assertEqual('foo', actual.node_uri)
        self.assertEqual('bar', actual.lane_uri)

    @async_test
    async def test_parse_synced_escaped(self):
        # Given
        message = '@synced(node: "foo/bar", lane: "lane/uri/test")'
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual('synced', actual.tag)
        self.assertEqual('foo/bar', actual.node_uri)
        self.assertEqual('lane/uri/test', actual.lane_uri)

    @async_test
    async def test_parse_synced_body_int(self):
        # Given
        message = '@synced(node: foo, lane: bar)33'
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual('synced', actual.tag)
        self.assertEqual('foo', actual.node_uri)
        self.assertEqual('bar', actual.lane_uri)
        self.assertEqual(33, actual.body.value)

    @async_test
    async def test_parse_synced_body_float(self):
        # Given
        message = '@synced(node: foo, lane: bar)37.13'
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual('synced', actual.tag)
        self.assertEqual('foo', actual.node_uri)
        self.assertEqual('bar', actual.lane_uri)
        self.assertEqual(37.13, actual.body.value)

    @async_test
    async def test_parse_synced_body_bool(self):
        # Given
        message = '@synced(node: foo, lane: bar)true'
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual('synced', actual.tag)
        self.assertEqual('foo', actual.node_uri)
        self.assertEqual('bar', actual.lane_uri)
        self.assertEqual(True, actual.body.value)

    @async_test
    async def test_parse_synced_body_string(self):
        # Given
        message = '@synced(node: foo, lane: bar)"Hello, World"'
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual('synced', actual.tag)
        self.assertEqual('foo', actual.node_uri)
        self.assertEqual('bar', actual.lane_uri)
        self.assertEqual('Hello, World', actual.body.value)

    @async_test
    async def test_parse_linked(self):
        # Given
        message = '@linked(node: foo, lane: bar)'
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual('linked', actual.tag)
        self.assertEqual('foo', actual.node_uri)
        self.assertEqual('bar', actual.lane_uri)

    @async_test
    async def test_parse_linked_escaped(self):
        # Given
        message = '@linked(node: "bar/baz/2", lane: "foo/bar")'
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual('linked', actual.tag)
        self.assertEqual('bar/baz/2', actual.node_uri)
        self.assertEqual('foo/bar', actual.lane_uri)

    @async_test
    async def test_parse_linked_body_int(self):
        # Given
        message = '@linked(node: "bar/baz/2", lane: "foo/bar")9999999'
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual('linked', actual.tag)
        self.assertEqual('bar/baz/2', actual.node_uri)
        self.assertEqual('foo/bar', actual.lane_uri)
        self.assertEqual(9999999, actual.body.value)

    @async_test
    async def test_parse_linked_body_float(self):
        # Given
        message = '@linked(node: "bar/baz/2", lane: "foo/bar")-0.00031'
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual('linked', actual.tag)
        self.assertEqual('bar/baz/2', actual.node_uri)
        self.assertEqual('foo/bar', actual.lane_uri)
        self.assertEqual(-0.00031, actual.body.value)

    @async_test
    async def test_parse_linked_body_bool(self):
        # Given
        message = '@linked(node: "bar/baz/2", lane: "foo/bar")false'
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual('linked', actual.tag)
        self.assertEqual('bar/baz/2', actual.node_uri)
        self.assertEqual('foo/bar', actual.lane_uri)
        self.assertEqual(False, actual.body.value)

    @async_test
    async def test_parse_linked_body_string(self):
        # Given
        message = '@linked(node: "bar/baz/2", lane: "foo/bar")"Hello, World"'
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual('linked', actual.tag)
        self.assertEqual('bar/baz/2', actual.node_uri)
        self.assertEqual('foo/bar', actual.lane_uri)
        self.assertEqual('Hello, World', actual.body.value)

    @async_test
    async def test_parse_linked_prio(self):
        # Given
        message = '@linked(node: foo, lane: bar, prio: 1000.3)'
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual('foo', actual.node_uri)
        self.assertEqual('bar', actual.lane_uri)
        self.assertEqual(1000.3, actual.prio)

    @async_test
    async def test_parse_linked_rate(self):
        # Given
        message = '@linked(node: "foo", lane: "1/bar/", rate: 33)'
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual('foo', actual.node_uri)
        self.assertEqual('1/bar/', actual.lane_uri)
        self.assertEqual(33, actual.rate)

    @async_test
    async def test_parse_linked_prio_rate(self):
        # Given
        message = '@linked(node: foo, lane: bar, prio: 13, rate: 37)'
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual('foo', actual.node_uri)
        self.assertEqual('bar', actual.lane_uri)
        self.assertEqual(13, actual.prio)
        self.assertEqual(37, actual.rate)

    @async_test
    async def test_parse_command(self):
        # Given
        message = '@command(node: foo, lane: bar)'
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual('command', actual.tag)
        self.assertEqual('foo', actual.node_uri)
        self.assertEqual('bar', actual.lane_uri)

    @async_test
    async def test_parse_command_escaped(self):
        # Given
        message = '@command(node: "foo/bar", lane: "lane/uri/test")'
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual('command', actual.tag)
        self.assertEqual('foo/bar', actual.node_uri)
        self.assertEqual('lane/uri/test', actual.lane_uri)

    @async_test
    async def test_parse_command_body_int(self):
        # Given
        message = '@command(node: "foo/bar", lane: "lane/uri/test")-24'
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual('command', actual.tag)
        self.assertEqual('foo/bar', actual.node_uri)
        self.assertEqual('lane/uri/test', actual.lane_uri)
        self.assertEqual(-24, actual.body.value)

    @async_test
    async def test_parse_command_body_float(self):
        # Given
        message = '@command(node: "foo/bar", lane: "lane/uri/test")-0.5'
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual('command', actual.tag)
        self.assertEqual('foo/bar', actual.node_uri)
        self.assertEqual('lane/uri/test', actual.lane_uri)
        self.assertEqual(-0.5, actual.body.value)

    @async_test
    async def test_parse_command_body_bool(self):
        # Given
        message = '@command(node: "foo/bar", lane: "lane/uri/test")true'
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual('command', actual.tag)
        self.assertEqual('foo/bar', actual.node_uri)
        self.assertEqual('lane/uri/test', actual.lane_uri)
        self.assertEqual(True, actual.body.value)

    @async_test
    async def test_parse_command_body_string(self):
        # Given
        message = '@command(node: "foo/bar", lane: "lane/uri/test")"0.32"'
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual('command', actual.tag)
        self.assertEqual('foo/bar', actual.node_uri)
        self.assertEqual('lane/uri/test', actual.lane_uri)
        self.assertEqual('0.32', actual.body.value)

    @async_test
    async def test_parse_command_body_remove(self):
        # Given
        message = '@command(node:"/unit/foo",lane:shoppingCart)@remove(key:FromClientLink)'
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual('command', actual.tag)
        self.assertEqual('/unit/foo', actual.node_uri)
        self.assertEqual('shoppingCart', actual.lane_uri)
        self.assertEqual('remove', actual.body.items[0].key.value)
        self.assertEqual('key', actual.body.items[0].value.items[0].key.value)
        self.assertEqual('FromClientLink', actual.body.items[0].value.items[0].value.value)

    @async_test
    async def test_parse_event(self):
        # Given
        message = '@event(node: foo, lane: bar)'
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual('event', actual.tag)
        self.assertEqual('foo', actual.node_uri)
        self.assertEqual('bar', actual.lane_uri)

    @async_test
    async def test_parse_event_escaped(self):
        # Given
        message = '@event(node: "bar/baz/2", lane: "foo/bar")'
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual('event', actual.tag)
        self.assertEqual('bar/baz/2', actual.node_uri)
        self.assertEqual('foo/bar', actual.lane_uri)

    @async_test
    async def test_parse_event_body_int(self):
        # Given
        message = '@event(node: "bar/baz/2", lane: "foo/bar")332'
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual('event', actual.tag)
        self.assertEqual('bar/baz/2', actual.node_uri)
        self.assertEqual('foo/bar', actual.lane_uri)
        self.assertEqual(332, actual.body.value)

    @async_test
    async def test_parse_event_body_float(self):
        # Given
        message = '@event(node: "bar/baz/2", lane: "foo/bar")0.1'
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual('event', actual.tag)
        self.assertEqual('bar/baz/2', actual.node_uri)
        self.assertEqual('foo/bar', actual.lane_uri)
        self.assertEqual(0.1, actual.body.value)

    @async_test
    async def test_parse_event_body_bool(self):
        # Given
        message = '@event(node: "bar/baz/2", lane: "foo/bar")true'
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual('event', actual.tag)
        self.assertEqual('bar/baz/2', actual.node_uri)
        self.assertEqual('foo/bar', actual.lane_uri)
        self.assertEqual(True, actual.body.value)

    @async_test
    async def test_parse_event_body_string(self):
        # Given
        message = '@event(node: "bar/baz/2", lane: "foo/bar")"Hello, World"'
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual('event', actual.tag)
        self.assertEqual('bar/baz/2', actual.node_uri)
        self.assertEqual('foo/bar', actual.lane_uri)
        self.assertEqual('Hello, World', actual.body.value)

    @async_test
    async def test_parse_event_body_object(self):
        # Given
        message = '@event(node: "bar/baz/2", lane: "foo/bar")@Person{name:Bar,age:14,salary:5.9}'
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual('event', actual.tag)
        self.assertEqual('bar/baz/2', actual.node_uri)
        self.assertEqual('foo/bar', actual.lane_uri)

        self.assertEqual(4, len(actual.body.items))
        self.assertEqual('Person', actual.body.items[0].key.value)
        self.assertEqual('name', actual.body.items[1].key.value)
        self.assertEqual('Bar', actual.body.items[1].value.value)
        self.assertEqual('age', actual.body.items[2].key.value)
        self.assertEqual(14, actual.body.items[2].value.value)
        self.assertEqual('salary', actual.body.items[3].key.value)
        self.assertEqual(5.9, actual.body.items[3].value.value)

    @async_test
    async def test_parse_event_body_nested(self):
        # Given
        message = '@event(node: "bar/baz/2", lane: "foo/bar")@Person{name:Par,age:11,salary:5.9,friend:@Person{name:Foo,age:18,salary:99.9}'
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual('event', actual.tag)
        self.assertEqual('bar/baz/2', actual.node_uri)
        self.assertEqual('foo/bar', actual.lane_uri)

        self.assertEqual(5, len(actual.body.items))
        self.assertEqual('Person', actual.body.items[0].key.value)
        self.assertEqual('name', actual.body.items[1].key.value)
        self.assertEqual('Par', actual.body.items[1].value.value)
        self.assertEqual('age', actual.body.items[2].key.value)
        self.assertEqual(11, actual.body.items[2].value.value)
        self.assertEqual('salary', actual.body.items[3].key.value)
        self.assertEqual(5.9, actual.body.items[3].value.value)
        self.assertEqual('friend', actual.body.items[4].key.value)
        self.assertEqual(4, len(actual.body.items[4].value.items))
        self.assertEqual('Person', actual.body.items[4].value.items[0].key.value)
        self.assertEqual('name', actual.body.items[4].value.items[1].key.value)
        self.assertEqual('Foo', actual.body.items[4].value.items[1].value.value)
        self.assertEqual('age', actual.body.items[4].value.items[2].key.value)
        self.assertEqual(18, actual.body.items[4].value.items[2].value.value)
        self.assertEqual('salary', actual.body.items[4].value.items[3].key.value)
        self.assertEqual(99.9, actual.body.items[4].value.items[3].value.value)
