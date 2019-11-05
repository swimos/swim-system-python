import math
import unittest

from swimai import Value, Text, RecordMap, Slot, Attr, Num
from swimai.warp.warp import SyncedResponseForm, SyncedResponse, SyncRequestForm, SyncRequest, LinkedResponseForm, CommandMessageForm, \
    EventMessageForm, LinkedResponse, CommandMessage, EventMessage


class TestForms(unittest.TestCase):

    def test_lane_addressed_form_mold_empty(self):
        # Given
        envelope = None
        form = SyncedResponseForm()
        # When
        actual = form.mold(envelope)
        # Then
        self.assertEqual(Value.extant(), actual)

    def test_lane_addressed_form_cast_missing_headers(self):
        # Given
        form = SyncedResponseForm()
        items = RecordMap.create()
        record_map = RecordMap.create()
        record_map.add(Attr.create_attr(Text.create_from('synced'), items))
        # When
        actual = form.cast(record_map)
        # Then
        self.assertEqual(None, actual)

    def test_lane_addressed_form_cast_missing_node(self):
        # Given
        form = SyncedResponseForm()
        items = RecordMap.create()
        items.add(Attr.create_attr(Text.create_from('lane'), Text.create_from('foo_lane')))
        record_map = RecordMap.create()
        record_map.add(Attr.create_attr(Text.create_from('synced'), items))
        # When
        actual = form.cast(record_map)
        # Then
        self.assertEqual(None, actual)

    def test_lane_addressed_form_cast_missing_lane(self):
        # Given
        form = SyncedResponseForm()
        items = RecordMap.create()
        items.add(Attr.create_attr(Text.create_from('node'), Text.create_from('foo_node')))
        record_map = RecordMap.create()
        record_map.add(Attr.create_attr(Text.create_from('synced'), items))
        # When
        actual = form.cast(record_map)
        # Then
        self.assertEqual(None, actual)

    def test_link_addressed_form_mold_empty(self):
        # Given
        envelope = None
        form = SyncRequestForm()
        # When
        actual = form.mold(envelope)
        # Then
        self.assertEqual(Value.extant(), actual)

    def test_link_addressed_form_mold_prio_zero(self):
        # Given
        envelope = SyncRequest('node_foo', 'lane_bar', prio=0, rate=2.5)
        form = SyncRequestForm()
        # When
        actual = form.mold(envelope)
        # Then
        self.assertIsInstance(actual, RecordMap)
        self.assertEqual('node_foo', actual.get_item(0).value.get_item(0).value.value)
        self.assertEqual('lane_bar', actual.get_item(0).value.get_item(1).value.value)
        self.assertEqual('rate', actual.get_item(0).value.get_item(2).key.value)
        self.assertEqual(2.5, actual.get_item(0).value.get_item(2).value.value)

    def test_link_addressed_form_mold_prio_nan(self):
        # Given
        envelope = SyncRequest('synced_node', 'synced_lane', prio=math.nan, rate=3.4)
        form = SyncRequestForm()
        # When
        actual = form.mold(envelope)
        # Then
        self.assertIsInstance(actual, RecordMap)
        self.assertEqual('synced_node', actual.get_item(0).value.get_item(0).value.value)
        self.assertEqual('synced_lane', actual.get_item(0).value.get_item(1).value.value)
        self.assertEqual('rate', actual.get_item(0).value.get_item(2).key.value)
        self.assertEqual(3.4, actual.get_item(0).value.get_item(2).value.value)

    def test_link_addressed_form_mold_rate_zero(self):
        # Given
        envelope = SyncRequest('node_rate_foo', 'lane_rate_bar', prio=2.1, rate=0)
        form = SyncRequestForm()
        # When
        actual = form.mold(envelope)
        # Then
        self.assertIsInstance(actual, RecordMap)
        self.assertEqual('node_rate_foo', actual.get_item(0).value.get_item(0).value.value)
        self.assertEqual('lane_rate_bar', actual.get_item(0).value.get_item(1).value.value)
        self.assertEqual('prio', actual.get_item(0).value.get_item(2).key.value)
        self.assertEqual(2.1, actual.get_item(0).value.get_item(2).value.value)

    def test_link_addressed_form_mold_rate_nan(self):
        # Given
        envelope = SyncRequest('node_baz', 'lane_qux', prio=13.4, rate=math.nan)
        form = SyncRequestForm()
        # When
        actual = form.mold(envelope)
        # Then
        self.assertIsInstance(actual, RecordMap)
        self.assertEqual('node_baz', actual.get_item(0).value.get_item(0).value.value)
        self.assertEqual('lane_qux', actual.get_item(0).value.get_item(1).value.value)
        self.assertEqual('prio', actual.get_item(0).value.get_item(2).key.value)
        self.assertEqual(13.4, actual.get_item(0).value.get_item(2).value.value)

    def test_link_addressed_cast_missing_headers(self):
        # Given
        form = SyncRequestForm()
        items = RecordMap.create()
        record_map = RecordMap.create()
        record_map.add(Attr.create_attr(Text.create_from('sync'), items))
        # When
        actual = form.cast(record_map)
        # Then
        self.assertEqual(None, actual)

    def test_link_addressed_form_cast_missing_node(self):
        # Given
        form = SyncRequestForm()
        items = RecordMap.create()
        items.add(Attr.create_attr(Text.create_from('lane'), Text.create_from('sync_foo_lane')))
        record_map = RecordMap.create()
        record_map.add(Attr.create_attr(Text.create_from('sync'), items))
        # When
        actual = form.cast(record_map)
        # Then
        self.assertEqual(None, actual)

    def test_link_addressed_form_cast_missing_lane(self):
        # Given
        form = SyncRequestForm()
        items = RecordMap.create()
        items.add(Attr.create_attr(Text.create_from('node'), Text.create_from('sync_foo_node')))
        record_map = RecordMap.create()
        record_map.add(Attr.create_attr(Text.create_from('sync'), items))
        # When
        actual = form.cast(record_map)
        # Then
        self.assertEqual(None, actual)

    def test_synced_form(self):
        # Given
        actual = SyncedResponseForm()
        # Then
        self.assertIsInstance(actual, SyncedResponseForm)
        self.assertEqual('synced', actual.tag)

    def test_synced_form_create_envelope(self):
        # Given
        form = SyncedResponseForm()
        body = Text.create_from('synced_body')
        # When
        actual = form.create_envelope_from('foo', 'bar', body)
        # Then
        self.assertIsInstance(actual, SyncedResponse)
        self.assertEqual('foo', actual.node_uri)
        self.assertEqual('bar', actual.lane_uri)
        self.assertEqual(body, actual.body)

    def test_synced_form_mold(self):
        # Given
        form = SyncedResponseForm()
        envelope = SyncedResponse('foo_node', 'bar_lane', body=Text.create_from('Boo'))
        # When
        actual = form.mold(envelope)
        # Then
        self.assertIsInstance(actual, RecordMap)
        self.assertEqual(2, actual.size)
        self.assertEqual('synced', actual.tag)
        self.assertEqual('foo_node', actual.get_item(0).value.get_item(0).value.value)
        self.assertEqual('bar_lane', actual.get_item(0).value.get_item(1).value.value)
        self.assertEqual('Boo', actual.get_item(1).value)

    def test_synced_form_cast(self):
        # Given
        form = SyncedResponseForm()
        items = RecordMap.create()
        items.add(Slot.create_slot(Text.create_from('node'), Text.create_from('synced_node')))
        items.add(Slot.create_slot(Text.create_from('lane'), Text.create_from('synced_lane')))
        body = Attr.create_attr(Text.create_from('body'), Text.create_from('synced_body'))
        record_map = RecordMap.create()
        record_map.add(Attr.create_attr(Text.create_from('synced'), items))
        record_map.add(body)
        # When
        actual = form.cast(record_map)
        # Then
        self.assertIsInstance(actual, SyncedResponse)
        self.assertEqual('synced_node', actual.node_uri)
        self.assertEqual('synced_lane', actual.lane_uri)
        self.assertEqual(body, actual.body.get_item(0))

    def test_sync_form(self):
        # Given
        actual = SyncRequestForm()
        # Then
        self.assertIsInstance(actual, SyncRequestForm)
        self.assertEqual('sync', actual.tag)

    def test_sync_form_create_envelope(self):
        # Given
        form = SyncRequestForm()
        body = Text.create_from('sync_body')
        # When
        actual = form.create_envelope_from('foo', 'bar', prio=3.2, rate=2.1, body=body)
        # Then
        self.assertIsInstance(actual, SyncRequest)
        self.assertEqual('foo', actual.node_uri)
        self.assertEqual('bar', actual.lane_uri)
        self.assertEqual(3.2, actual.prio)
        self.assertEqual(2.1, actual.rate)
        self.assertEqual(body, actual.body)

    def test_sync_form_mold(self):
        # Given
        form = SyncRequestForm()
        envelope = SyncRequest('sync_node', 'sync_lane', prio=99.1, rate=41.42, body=Text.create_from('Moo'))
        # When
        actual = form.mold(envelope)
        # Then
        self.assertIsInstance(actual, RecordMap)
        self.assertEqual(2, actual.size)
        self.assertEqual('sync', actual.tag)
        self.assertEqual('sync_node', actual.get_item(0).value.get_item(0).value.value)
        self.assertEqual('sync_lane', actual.get_item(0).value.get_item(1).value.value)
        self.assertEqual(99.1, actual.get_item(0).value.get_item(2).value.value)
        self.assertEqual(41.42, actual.get_item(0).value.get_item(3).value.value)
        self.assertEqual('Moo', actual.get_item(1).value)

    def test_sync_form_cast(self):
        # Given
        form = SyncRequestForm()
        items = RecordMap.create()
        items.add(Slot.create_slot(Text.create_from('node'), Text.create_from('sync_node')))
        items.add(Slot.create_slot(Text.create_from('lane'), Text.create_from('sync_lane')))
        items.add(Slot.create_slot(Text.create_from('prio'), Num.create_from(33.12)))
        items.add(Slot.create_slot(Text.create_from('rate'), Num.create_from(12.33)))
        body = Attr.create_attr(Text.create_from('body'), Text.create_from('sync_body'))
        record_map = RecordMap.create()
        record_map.add(Attr.create_attr(Text.create_from('sync'), items))
        record_map.add(body)
        # When
        actual = form.cast(record_map)
        # Then
        self.assertIsInstance(actual, SyncRequest)
        self.assertEqual('sync_node', actual.node_uri)
        self.assertEqual('sync_lane', actual.lane_uri)
        self.assertEqual(33.12, actual.prio)
        self.assertEqual(12.33, actual.rate)
        self.assertEqual(body, actual.body.get_item(0))

    def test_linked_form(self):
        # Given
        actual = LinkedResponseForm()
        # Then
        self.assertIsInstance(actual, LinkedResponseForm)
        self.assertEqual('linked', actual.tag)

    def test_linked_form_create_envelope(self):
        # Given
        form = LinkedResponseForm()
        body = Text.create_from('linked_body')
        # When
        actual = form.create_envelope_from('boo', 'far', prio=1.13, rate=2.26, body=body)
        # Then
        self.assertIsInstance(actual, LinkedResponse)
        self.assertEqual('boo', actual.node_uri)
        self.assertEqual('far', actual.lane_uri)
        self.assertEqual(1.13, actual.prio)
        self.assertEqual(2.26, actual.rate)
        self.assertEqual(body, actual.body)

    def test_linked_form_mold(self):
        # Given
        form = LinkedResponseForm()
        envelope = LinkedResponse('linked_node', 'linked_lane', prio=13, rate=15, body=Text.create_from('Foo'))
        # When
        actual = form.mold(envelope)
        # Then
        self.assertIsInstance(actual, RecordMap)
        self.assertEqual(2, actual.size)
        self.assertEqual('linked', actual.tag)
        self.assertEqual('linked_node', actual.get_item(0).value.get_item(0).value.value)
        self.assertEqual('linked_lane', actual.get_item(0).value.get_item(1).value.value)
        self.assertEqual(13, actual.get_item(0).value.get_item(2).value.value)
        self.assertEqual(15, actual.get_item(0).value.get_item(3).value.value)
        self.assertEqual('Foo', actual.get_item(1).value)

    def test_linked_form_cast(self):
        # Given
        form = LinkedResponseForm()
        items = RecordMap.create()
        items.add(Slot.create_slot(Text.create_from('node'), Text.create_from('linked_node')))
        items.add(Slot.create_slot(Text.create_from('lane'), Text.create_from('linked_lane')))
        items.add(Slot.create_slot(Text.create_from('prio'), Num.create_from(14)))
        items.add(Slot.create_slot(Text.create_from('rate'), Num.create_from(13)))
        body = Attr.create_attr(Text.create_from('body'), Text.create_from('linked_body'))
        record_map = RecordMap.create()
        record_map.add(Attr.create_attr(Text.create_from('linked'), items))
        record_map.add(body)
        # When
        actual = form.cast(record_map)
        # Then
        self.assertIsInstance(actual, LinkedResponse)
        self.assertEqual('linked_node', actual.node_uri)
        self.assertEqual('linked_lane', actual.lane_uri)
        self.assertEqual(14, actual.prio)
        self.assertEqual(13, actual.rate)
        self.assertEqual(body, actual.body.get_item(0))

    def test_command_form(self):
        # Given
        actual = CommandMessageForm()
        # Then
        self.assertIsInstance(actual, CommandMessageForm)
        self.assertEqual('command', actual.tag)

    def test_command_form_create_envelope(self):
        # Given
        form = CommandMessageForm()
        body = Text.create_from('message_body')
        # When
        actual = form.create_envelope_from('message_foo', 'message_bar', body=body)
        # Then
        self.assertIsInstance(actual, CommandMessage)
        self.assertEqual('message_foo', actual.node_uri)
        self.assertEqual('message_bar', actual.lane_uri)
        self.assertEqual(body, actual.body)

    def test_command_form_mold(self):
        # Given
        form = CommandMessageForm()
        envelope = CommandMessage('command_node', 'command_lane', body=Text.create_from('Command_body'))
        # When
        actual = form.mold(envelope)
        # Then
        self.assertIsInstance(actual, RecordMap)
        self.assertEqual(2, actual.size)
        self.assertEqual('command', actual.tag)
        self.assertEqual('command_node', actual.get_item(0).value.get_item(0).value.value)
        self.assertEqual('command_lane', actual.get_item(0).value.get_item(1).value.value)
        self.assertEqual('Command_body', actual.get_item(1).value)

    def test_command_form_cast(self):
        # Given
        form = CommandMessageForm()
        items = RecordMap.create()
        items.add(Slot.create_slot(Text.create_from('node'), Text.create_from('command_node')))
        items.add(Slot.create_slot(Text.create_from('lane'), Text.create_from('command_lane')))
        body = Attr.create_attr(Text.create_from('body'), Text.create_from('command_body'))
        record_map = RecordMap.create()
        record_map.add(Attr.create_attr(Text.create_from('command'), items))
        record_map.add(body)
        # When
        actual = form.cast(record_map)
        # Then
        self.assertIsInstance(actual, CommandMessage)
        self.assertEqual('command_node', actual.node_uri)
        self.assertEqual('command_lane', actual.lane_uri)
        self.assertEqual(body, actual.body.get_item(0))

    def test_event_form(self):
        # Given
        actual = EventMessageForm()
        # Then
        self.assertIsInstance(actual, EventMessageForm)
        self.assertEqual('event', actual.tag)

    def test_event_form_create_envelope(self):
        # Given
        form = EventMessageForm()
        body = Text.create_from('event_body')
        # When
        actual = form.create_envelope_from('event_foo', 'event_bar', body=body)
        # Then
        self.assertIsInstance(actual, EventMessage)
        self.assertEqual('event_foo', actual.node_uri)
        self.assertEqual('event_bar', actual.lane_uri)
        self.assertEqual(body, actual.body)

    def test_event_form_mold(self):
        # Given
        form = EventMessageForm()
        envelope = EventMessage('event_node', 'event_lane', body=Text.create_from('Event_body'))
        # When
        actual = form.mold(envelope)
        # Then
        self.assertIsInstance(actual, RecordMap)
        self.assertEqual(2, actual.size)
        self.assertEqual('event', actual.tag)
        self.assertEqual('event_node', actual.get_item(0).value.get_item(0).value.value)
        self.assertEqual('event_lane', actual.get_item(0).value.get_item(1).value.value)
        self.assertEqual('Event_body', actual.get_item(1).value)

    def test_event_form_cast(self):
        # Given
        form = EventMessageForm()
        items = RecordMap.create()
        items.add(Slot.create_slot(Text.create_from('node'), Text.create_from('event_node')))
        items.add(Slot.create_slot(Text.create_from('lane'), Text.create_from('event_lane')))
        body = Attr.create_attr(Text.create_from('body'), Text.create_from('event_body'))
        record_map = RecordMap.create()
        record_map.add(Attr.create_attr(Text.create_from('event'), items))
        record_map.add(body)
        # When
        actual = form.cast(record_map)
        # Then
        self.assertIsInstance(actual, EventMessage)
        self.assertEqual('event_node', actual.node_uri)
        self.assertEqual('event_lane', actual.lane_uri)
        self.assertEqual(body, actual.body.get_item(0))
