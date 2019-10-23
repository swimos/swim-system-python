import asyncio
import unittest

from aiounittest import async_test
from swim.structures.structs import Num, Text, RecordMap, Attr, Slot
from swim.warp.warp import Envelope, SyncedResponse, CommandMessage, SyncRequest, LinkedResponse, EventMessage


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
    async def test_parse_linked(self):
        # Given
        message = '@linked(node: foo, lane: bar)'
        expected = LinkedResponse('foo', 'bar')
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual(expected.tag, actual.tag)
        self.assertEqual(expected.node_uri, actual.node_uri)
        self.assertEqual(expected.lane_uri, actual.lane_uri)

    @async_test
    async def test_parse_linked_escaped(self):
        # Given
        message = '@linked(node: "bar/baz/2", lane: "foo/bar")'
        expected = LinkedResponse('bar/baz/2', 'foo/bar')
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual(expected.tag, actual.tag)
        self.assertEqual(expected.node_uri, actual.node_uri)
        self.assertEqual(expected.lane_uri, actual.lane_uri)

    @async_test
    async def test_parse_linked_body_int(self):
        # Given
        message = '@linked(node: "bar/baz/2", lane: "foo/bar")9999999'
        expected = LinkedResponse('bar/baz/2', 'foo/bar', body=Num.create_from(9999999))
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual(expected.tag, actual.tag)
        self.assertEqual(expected.node_uri, actual.node_uri)
        self.assertEqual(expected.lane_uri, actual.lane_uri)
        self.assertEqual(expected.body.value, actual.body.value)

    @async_test
    async def test_parse_linked_body_float(self):
        # Given
        message = '@linked(node: "bar/baz/2", lane: "foo/bar")-0.00031'
        expected = LinkedResponse('bar/baz/2', 'foo/bar', body=Num.create_from(-0.00031))
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual(expected.tag, actual.tag)
        self.assertEqual(expected.node_uri, actual.node_uri)
        self.assertEqual(expected.lane_uri, actual.lane_uri)
        self.assertEqual(expected.body.value, actual.body.value)

    @async_test
    async def test_parse_linked_body_string(self):
        # Given
        message = '@linked(node: "bar/baz/2", lane: "foo/bar")"Hello, World"'
        expected = LinkedResponse('bar/baz/2', 'foo/bar', body=Text.create_from('Hello, World'))
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual(expected.tag, actual.tag)
        self.assertEqual(expected.node_uri, actual.node_uri)
        self.assertEqual(expected.lane_uri, actual.lane_uri)
        self.assertEqual(expected.body.value, actual.body.value)

    @async_test
    async def test_parse_linked_prio(self):
        # Given
        message = '@linked(node: foo, lane: bar, prio: 1000.3)'
        expected = LinkedResponse('foo', 'bar', prio=1000.3)
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual(expected.node_uri, actual.node_uri)
        self.assertEqual(expected.lane_uri, actual.lane_uri)
        self.assertEqual(expected.prio, actual.prio)

    @async_test
    async def test_parse_linked_rate(self):
        # Given
        message = '@linked(node: "foo", lane: "1/bar/", rate: 33)'
        expected = LinkedResponse('foo', '1/bar/', rate=33)
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual(expected.node_uri, actual.node_uri)
        self.assertEqual(expected.lane_uri, actual.lane_uri)
        self.assertEqual(expected.rate, actual.rate)

    @async_test
    async def test_parse_linked_prio_rate(self):
        # Given
        message = '@linked(node: foo, lane: bar, prio: 13, rate: 37)'
        expected = LinkedResponse('foo', 'bar', prio=13, rate=37)
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual(expected.node_uri, actual.node_uri)
        self.assertEqual(expected.lane_uri, actual.lane_uri)
        self.assertEqual(expected.prio, actual.prio)
        self.assertEqual(expected.rate, actual.rate)

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
        expected = CommandMessage('/unit/foo', 'shoppingCart',
                                  body=RecordMap.of(
                                      Attr.of(Text.create_from('remove'),
                                              RecordMap.of(Slot.of(Text.create_from('key'), Text.create_from('FromClientLink'))))))

        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual(expected.tag, actual.tag)
        self.assertEqual(expected.node_uri, actual.node_uri)
        self.assertEqual(expected.lane_uri, actual.lane_uri)
        self.assertEqual(expected.body.items[0].key.value, actual.body.items[0].key.value)
        self.assertEqual(expected.body.items[0].value.items[0].key.value, actual.body.items[0].value.items[0].key.value)
        self.assertEqual(expected.body.items[0].value.items[0].value.value, actual.body.items[0].value.items[0].value.value)

    @async_test
    async def test_parse_event(self):
        # Given
        message = '@event(node: foo, lane: bar)'
        expected = EventMessage('foo', 'bar')
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual(expected.tag, actual.tag)
        self.assertEqual(expected.node_uri, actual.node_uri)
        self.assertEqual(expected.lane_uri, actual.lane_uri)

    @async_test
    async def test_parse_event_escaped(self):
        # Given
        message = '@event(node: "bar/baz/2", lane: "foo/bar")'
        expected = EventMessage('bar/baz/2', 'foo/bar')
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual(expected.tag, actual.tag)
        self.assertEqual(expected.node_uri, actual.node_uri)
        self.assertEqual(expected.lane_uri, actual.lane_uri)

    @async_test
    async def test_parse_event_body_int(self):
        # Given
        message = '@event(node: "bar/baz/2", lane: "foo/bar")332'
        expected = EventMessage('bar/baz/2', 'foo/bar', body=Num.create_from(332))
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual(expected.tag, actual.tag)
        self.assertEqual(expected.node_uri, actual.node_uri)
        self.assertEqual(expected.lane_uri, actual.lane_uri)
        self.assertEqual(expected.body.value, actual.body.value)

    @async_test
    async def test_parse_event_body_float(self):
        # Given
        message = '@event(node: "bar/baz/2", lane: "foo/bar")0.1'
        expected = EventMessage('bar/baz/2', 'foo/bar', body=Num.create_from(0.1))
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual(expected.tag, actual.tag)
        self.assertEqual(expected.node_uri, actual.node_uri)
        self.assertEqual(expected.lane_uri, actual.lane_uri)
        self.assertEqual(expected.body.value, actual.body.value)

    @async_test
    async def test_parse_event_body_string(self):
        # Given
        message = '@event(node: "bar/baz/2", lane: "foo/bar")"Hello, World"'
        expected = EventMessage('bar/baz/2', 'foo/bar', body=Text.create_from('Hello, World'))
        # When
        requests = await asyncio.gather(Envelope.parse_recon(message))
        actual = requests[0]
        # Then
        self.assertEqual(expected.tag, actual.tag)
        self.assertEqual(expected.node_uri, actual.node_uri)
        self.assertEqual(expected.lane_uri, actual.lane_uri)
        self.assertEqual(expected.body.value, actual.body.value)

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
        message = '@event(node: "bar/baz/2", lane: "foo/bar")@Person{name:Bar,age:14,salary:5.9,friend:@Person{name:Foo,age:18,salary:99.9}'
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
        self.assertEqual('Bar', actual.body.items[1].value.value)
        self.assertEqual('age', actual.body.items[2].key.value)
        self.assertEqual(14, actual.body.items[2].value.value)
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
