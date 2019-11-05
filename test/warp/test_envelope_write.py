import asyncio
import unittest

from aiounittest import async_test
from swimai import Num, Text, RecordMap, Attr, Slot, Extant, Bool
from swimai.warp.warp import SyncRequest, SyncedResponse, EventMessage, LinkedResponse, CommandMessage


class TestWriters(unittest.TestCase):

    @async_test
    async def test_write_sync(self):
        # Given
        envelope = SyncRequest('foo', 'bar')
        expected = '@sync(node:foo,lane:bar)'

        # When
        responses = await asyncio.gather(envelope.to_recon())
        actual = responses[0]

        # Then
        self.assertEqual(expected, actual)

    @async_test
    async def test_write_sync_escaped(self):
        # Given
        envelope = SyncRequest('bar/baz/', 'foo/bar')
        expected = '@sync(node:"bar/baz/",lane:"foo/bar")'

        # When
        responses = await asyncio.gather(envelope.to_recon())
        actual = responses[0]

        # Then
        self.assertEqual(expected, actual)

    @async_test
    async def test_write_sync_body_int(self):
        # Given
        envelope = SyncRequest('bar/baz/', 'foo/bar', body=Num.create_from(42))
        expected = '@sync(node:"bar/baz/",lane:"foo/bar")42'

        # When
        responses = await asyncio.gather(envelope.to_recon())
        actual = responses[0]

        # Then
        self.assertEqual(expected, actual)

    @async_test
    async def test_write_sync_body_float(self):
        # Given
        envelope = SyncRequest('bar/baz/', 'foo/bar', body=Num.create_from(33.22))
        expected = '@sync(node:"bar/baz/",lane:"foo/bar")33.22'

        # When
        responses = await asyncio.gather(envelope.to_recon())
        actual = responses[0]

        # Then
        self.assertEqual(expected, actual)

    @async_test
    async def test_write_sync_body_bool(self):
        # Given
        envelope = SyncRequest('bar/baz/', 'foo/bar', body=Bool.create_from(False))
        expected = '@sync(node:"bar/baz/",lane:"foo/bar")false'

        # When
        responses = await asyncio.gather(envelope.to_recon())
        actual = responses[0]

        # Then
        self.assertEqual(expected, actual)

    @async_test
    async def test_write_sync_body_string(self):
        # Given
        envelope = SyncRequest('bar/baz/', 'foo/bar', body=Text.create_from('Hello, World!'))
        expected = '@sync(node:"bar/baz/",lane:"foo/bar")"Hello, World!"'

        # When
        responses = await asyncio.gather(envelope.to_recon())
        actual = responses[0]

        # Then
        self.assertEqual(expected, actual)

    @async_test
    async def test_write_sync_prio(self):
        # Given
        envelope = SyncRequest('bar/baz/', 'foo/bar', prio=33, body=Text.create_from('Hello, World!'))
        expected = '@sync(node:"bar/baz/",lane:"foo/bar",prio:33)"Hello, World!"'

        # When
        responses = await asyncio.gather(envelope.to_recon())
        actual = responses[0]

        # Then
        self.assertEqual(expected, actual)

    @async_test
    async def test_write_sync_rate(self):
        # Given
        envelope = SyncRequest('bar/baz/', 'foo/bar', rate=0.3, body=Text.create_from('Hello, World!'))
        expected = '@sync(node:"bar/baz/",lane:"foo/bar",rate:0.3)"Hello, World!"'

        # When
        responses = await asyncio.gather(envelope.to_recon())
        actual = responses[0]

        # Then
        self.assertEqual(expected, actual)

    @async_test
    async def test_write_sync_prio_rate(self):
        # Given
        envelope = SyncRequest('bar/baz/', 'foo/bar', prio=33.2, rate=0.3, body=Text.create_from('Hello, World!'))
        expected = '@sync(node:"bar/baz/",lane:"foo/bar",prio:33.2,rate:0.3)"Hello, World!"'

        # When
        responses = await asyncio.gather(envelope.to_recon())
        actual = responses[0]

        # Then
        self.assertEqual(expected, actual)

    @async_test
    async def test_write_synced(self):
        # Given
        envelope = SyncedResponse('foo', 'bar')
        expected = '@synced(node:foo,lane:bar)'

        # When
        responses = await asyncio.gather(envelope.to_recon())
        actual = responses[0]

        # Then
        self.assertEqual(expected, actual)

    @async_test
    async def test_write_synced_escaped(self):
        # Given
        envelope = SyncedResponse('foo/bar/baz', 'baz/bar/foo')
        expected = '@synced(node:"foo/bar/baz",lane:"baz/bar/foo")'

        # When
        responses = await asyncio.gather(envelope.to_recon())
        actual = responses[0]

        # Then
        self.assertEqual(expected, actual)

    @async_test
    async def test_write_synced_body_int(self):
        # Given
        envelope = SyncedResponse('foo/bar/baz', 'baz/bar/foo', body=Num.create_from(-13))
        expected = '@synced(node:"foo/bar/baz",lane:"baz/bar/foo")-13'

        # When
        responses = await asyncio.gather(envelope.to_recon())
        actual = responses[0]

        # Then
        self.assertEqual(expected, actual)

    @async_test
    async def test_write_synced_body_float(self):
        # Given
        envelope = SyncedResponse('foo/bar/baz', 'baz/bar/foo', body=Num.create_from(-13.04))
        expected = '@synced(node:"foo/bar/baz",lane:"baz/bar/foo")-13.04'

        # When
        responses = await asyncio.gather(envelope.to_recon())
        actual = responses[0]

        # Then
        self.assertEqual(expected, actual)

    @async_test
    async def test_write_synced_body_bool(self):
        # Given
        envelope = SyncedResponse('foo/bar/baz', 'baz/bar/foo', body=Bool.create_from(True))
        expected = '@synced(node:"foo/bar/baz",lane:"baz/bar/foo")true'

        # When
        responses = await asyncio.gather(envelope.to_recon())
        actual = responses[0]

        # Then
        self.assertEqual(expected, actual)

    @async_test
    async def test_write_synced_body_string(self):
        # Given
        envelope = SyncedResponse('foo/bar/baz', 'baz/bar/foo', body=Text.create_from('Hello, friend.'))
        expected = '@synced(node:"foo/bar/baz",lane:"baz/bar/foo")"Hello, friend."'

        # When
        responses = await asyncio.gather(envelope.to_recon())
        actual = responses[0]

        # Then
        self.assertEqual(expected, actual)

    @async_test
    async def test_write_linked(self):
        # Given
        envelope = LinkedResponse('test', 'foo')
        expected = '@linked(node:test,lane:foo)'

        # When
        responses = await asyncio.gather(envelope.to_recon())
        actual = responses[0]

        # Then
        self.assertEqual(expected, actual)

    @async_test
    async def test_write_linked_escaped(self):
        # Given
        envelope = LinkedResponse('/unit/5', '/unit/3')
        expected = '@linked(node:"/unit/5",lane:"/unit/3")'

        # When
        responses = await asyncio.gather(envelope.to_recon())
        actual = responses[0]

        # Then
        self.assertEqual(expected, actual)

    @async_test
    async def test_write_linked_body_int(self):
        # Given
        envelope = LinkedResponse('/unit/5', '/unit/3', body=Num.create_from(-100))
        expected = '@linked(node:"/unit/5",lane:"/unit/3")-100'

        # When
        responses = await asyncio.gather(envelope.to_recon())
        actual = responses[0]

        # Then
        self.assertEqual(expected, actual)

    @async_test
    async def test_write_linked_body_float(self):
        # Given
        envelope = LinkedResponse('/unit/5', '/unit/3', body=Num.create_from(-100.0))
        expected = '@linked(node:"/unit/5",lane:"/unit/3")-100.0'

        # When
        responses = await asyncio.gather(envelope.to_recon())
        actual = responses[0]

        # Then
        self.assertEqual(expected, actual)

    @async_test
    async def test_write_linked_body_bool(self):
        # Given
        envelope = LinkedResponse('/unit/5', '/unit/3', body=Bool.create_from(False))
        expected = '@linked(node:"/unit/5",lane:"/unit/3")false'

        # When
        responses = await asyncio.gather(envelope.to_recon())
        actual = responses[0]

        # Then
        self.assertEqual(expected, actual)

    @async_test
    async def test_write_linked_body_string(self):
        # Given
        envelope = LinkedResponse('/unit/5', '/unit/3', body=Text.create_from('spam and \\ham/'))
        expected = '@linked(node:"/unit/5",lane:"/unit/3")"spam and \\ham/"'

        # When
        responses = await asyncio.gather(envelope.to_recon())
        actual = responses[0]

        # Then
        self.assertEqual(expected, actual)

    @async_test
    async def test_write_linked_prio(self):
        # Given
        envelope = LinkedResponse('/unit/5', '/unit/3', prio=33.2, body=Text.create_from('spam and \\ham/'))
        expected = '@linked(node:"/unit/5",lane:"/unit/3",prio:33.2)"spam and \\ham/"'

        # When
        responses = await asyncio.gather(envelope.to_recon())
        actual = responses[0]

        # Then
        self.assertEqual(expected, actual)

    @async_test
    async def test_write_linked_rate(self):
        # Given
        envelope = LinkedResponse('/unit/5', '/unit/3', rate=0.2, body=Text.create_from('spam and \\ham/'))
        expected = '@linked(node:"/unit/5",lane:"/unit/3",rate:0.2)"spam and \\ham/"'

        # When
        responses = await asyncio.gather(envelope.to_recon())
        actual = responses[0]

        # Then
        self.assertEqual(expected, actual)

    @async_test
    async def test_write_linked_prio_rate(self):
        # Given
        envelope = LinkedResponse('/unit/5', '/unit/3', prio=22.11, rate=0.2, body=Text.create_from('spam and \\ham/'))
        expected = '@linked(node:"/unit/5",lane:"/unit/3",prio:22.11,rate:0.2)"spam and \\ham/"'

        # When
        responses = await asyncio.gather(envelope.to_recon())
        actual = responses[0]

        # Then
        self.assertEqual(expected, actual)

    @async_test
    async def test_write_command(self):
        # Given
        envelope = CommandMessage('test', 'foo')
        expected = '@command(node:test,lane:foo)'

        # When
        responses = await asyncio.gather(envelope.to_recon())
        actual = responses[0]

        # Then
        self.assertEqual(expected, actual)

    @async_test
    async def test_write_command_escaped(self):
        # Given
        envelope = CommandMessage('dead/parrot', 'spam/ham')
        expected = '@command(node:"dead/parrot",lane:"spam/ham")'

        # When
        responses = await asyncio.gather(envelope.to_recon())
        actual = responses[0]

        # Then
        self.assertEqual(expected, actual)

    @async_test
    async def test_write_command_body_int(self):
        # Given
        envelope = CommandMessage('dead/parrot', 'spam/ham', body=Num.create_from(911))
        expected = '@command(node:"dead/parrot",lane:"spam/ham")911'

        # When
        responses = await asyncio.gather(envelope.to_recon())
        actual = responses[0]

        # Then
        self.assertEqual(expected, actual)

    @async_test
    async def test_write_command_body_float(self):
        # Given
        envelope = CommandMessage('dead/parrot', 'spam/ham', body=Num.create_from(-911.119))
        expected = '@command(node:"dead/parrot",lane:"spam/ham")-911.119'

        # When
        responses = await asyncio.gather(envelope.to_recon())
        actual = responses[0]

        # Then
        self.assertEqual(expected, actual)

    @async_test
    async def test_write_command_body_bool(self):
        # Given
        envelope = CommandMessage('dead/parrot', 'spam/ham', body=Bool.create_from(True))
        expected = '@command(node:"dead/parrot",lane:"spam/ham")true'

        # When
        responses = await asyncio.gather(envelope.to_recon())
        actual = responses[0]

        # Then
        self.assertEqual(expected, actual)

    @async_test
    async def test_write_command_body_string(self):
        # Given
        envelope = CommandMessage('dead/parrot', 'spam/ham', body=Text.create_from('Polly the parrot.'))
        expected = '@command(node:"dead/parrot",lane:"spam/ham")"Polly the parrot."'

        # When
        responses = await asyncio.gather(envelope.to_recon())
        actual = responses[0]

        # Then
        self.assertEqual(expected, actual)

    @async_test
    async def test_write_command_body_remove(self):
        # Given
        envelope = CommandMessage('/unit/foo', 'shoppingCart',
                                  body=RecordMap.create_record_map(
                                      Attr.create_attr(Text.create_from('remove'),
                                                       RecordMap.create_record_map(
                                                           Slot.create_slot(Text.create_from('key'), Text.create_from('FromClientLink'))))))
        expected = '@command(node:"/unit/foo",lane:shoppingCart)@remove(key:FromClientLink)'

        # When
        responses = await asyncio.gather(envelope.to_recon())
        actual = responses[0]

        # Then
        self.assertEqual(expected, actual)

    @async_test
    async def test_write_event(self):
        # Given
        envelope = EventMessage('test', 'foo')
        expected = '@event(node:test,lane:foo)'

        # When
        responses = await asyncio.gather(envelope.to_recon())
        actual = responses[0]

        # Then
        self.assertEqual(expected, actual)

    @async_test
    async def test_write_event_escaped(self):
        # Given
        envelope = EventMessage('/this/is/spam', 'hello')
        expected = '@event(node:"/this/is/spam",lane:hello)'

        # When
        responses = await asyncio.gather(envelope.to_recon())
        actual = responses[0]

        # Then
        self.assertEqual(expected, actual)

    @async_test
    async def test_write_event_body_int(self):
        # Given
        envelope = EventMessage('/this/is/spam', 'hello', body=Num.create_from(1224))
        expected = '@event(node:"/this/is/spam",lane:hello)1224'

        # When
        responses = await asyncio.gather(envelope.to_recon())
        actual = responses[0]

        # Then
        self.assertEqual(expected, actual)

    @async_test
    async def test_write_event_body_float(self):
        # Given
        envelope = EventMessage('/this/is/spam', 'hello', body=Num.create_from(33.12))
        expected = '@event(node:"/this/is/spam",lane:hello)33.12'

        # When
        responses = await asyncio.gather(envelope.to_recon())
        actual = responses[0]

        # Then
        self.assertEqual(expected, actual)

    @async_test
    async def test_write_event_body_bool(self):
        # Given
        envelope = EventMessage('/this/is/spam', 'hello', body=Bool.create_from(False))
        expected = '@event(node:"/this/is/spam",lane:hello)false'

        # When
        responses = await asyncio.gather(envelope.to_recon())
        actual = responses[0]

        # Then
        self.assertEqual(expected, actual)

    @async_test
    async def test_write_event_body_string(self):
        # Given
        envelope = EventMessage('/this/is/spam', 'hello', body=Text.create_from("-33.12 / 6"))
        expected = '@event(node:"/this/is/spam",lane:hello)"-33.12 / 6"'

        # When
        responses = await asyncio.gather(envelope.to_recon())
        actual = responses[0]

        # Then
        self.assertEqual(expected, actual)

    @async_test
    async def test_write_event_body_object(self):
        # Given
        body = RecordMap.create()
        body.add(Attr.create_attr(Text.create_from('Person'), Extant.get_extant()))
        body.add(Slot.create_slot(Text.create_from('name'), Text.create_from('Bar')))
        body.add(Slot.create_slot(Text.create_from('age'), Num.create_from(14)))
        body.add(Slot.create_slot(Text.create_from('salary'), Num.create_from(-5.9)))

        envelope = EventMessage('/this/is/spam', 'hello', body=body)
        expected = '@event(node:"/this/is/spam",lane:hello)@Person{name:Bar,age:14,salary:-5.9}'

        # When
        responses = await asyncio.gather(envelope.to_recon())
        actual = responses[0]

        # Then
        self.assertEqual(expected, actual)

    @async_test
    async def test_write_event_body_nested(self):
        # Given

        friend = RecordMap.create()
        friend.add(Attr.create_attr(Text.create_from('Person'), Extant.get_extant()))
        friend.add(Slot.create_slot(Text.create_from('name'), Text.create_from('Sam/Spam')))
        friend.add(Slot.create_slot(Text.create_from('age'), Num.create_from(1)))
        friend.add(Slot.create_slot(Text.create_from('salary'), Num.create_from(22)))

        body = RecordMap.create()
        body.add(Attr.create_attr(Text.create_from('Person'), Extant.get_extant()))
        body.add(Slot.create_slot(Text.create_from('name'), Text.create_from('Par')))
        body.add(Slot.create_slot(Text.create_from('age'), Num.create_from(11)))
        body.add(Slot.create_slot(Text.create_from('salary'), Num.create_from(-5.9)))
        body.add(Slot.create_slot(Text.create_from('friend'), friend))

        envelope = EventMessage('/this/is/spam', 'hello', body=body)
        expected = '@event(node:"/this/is/spam",lane:hello)@Person{name:Par,age:11,salary:-5.9,friend:@Person{name:"Sam/Spam",age:1,salary:22}}'

        # When
        responses = await asyncio.gather(envelope.to_recon())
        actual = responses[0]

        # Then
        self.assertEqual(expected, actual)
