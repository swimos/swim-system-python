import unittest

from swimai import Absent, Text
from swimai.warp.warp import Envelope, SyncRequestForm, SyncedResponseForm, LinkedResponseForm, EventMessageForm, CommandMessageForm, SyncRequest, \
    SyncedResponse, LinkedResponse, CommandMessage, EventMessage


class TestEnvelopes(unittest.TestCase):

    def test_resolve_form_sync(self):
        # Given
        tag = 'sync'
        # When
        actual = Envelope.resolve_form(tag)
        # Then
        self.assertIsInstance(actual, SyncRequestForm)

    def test_resolve_form_synced(self):
        # Given
        tag = 'synced'
        # When
        actual = Envelope.resolve_form(tag)
        # Then
        self.assertIsInstance(actual, SyncedResponseForm)

    def test_resolve_form_linked(self):
        # Given
        tag = 'linked'
        # When
        actual = Envelope.resolve_form(tag)
        # Then
        self.assertIsInstance(actual, LinkedResponseForm)

    def test_resolve_form_event(self):
        # Given
        tag = 'event'
        # When
        actual = Envelope.resolve_form(tag)
        # Then
        self.assertIsInstance(actual, EventMessageForm)

    def test_resolve_form_command(self):
        # Given
        tag = 'command'
        # When
        actual = Envelope.resolve_form(tag)
        # Then
        self.assertIsInstance(actual, CommandMessageForm)

    def test_resolve_form_invalid(self):
        # Given
        tag = 'this_is_not_a_valid_form'
        # When
        with self.assertRaises(TypeError) as error:
            Envelope.resolve_form(tag)
        # Then
        message = error.exception.args[0]
        self.assertEqual(message, 'Invalid form tag: this_is_not_a_valid_form')

    def test_sync_request_empty_body(self):
        # Given
        node_uri = 'foo__sync_node'
        lane_uri = 'bar__sync_lane'
        # When
        actual = SyncRequest(node_uri, lane_uri)
        # Then
        self.assertEqual('foo__sync_node', actual.node_uri)
        self.assertEqual('bar__sync_lane', actual.lane_uri)
        self.assertEqual(0.0, actual.prio)
        self.assertEqual(0.0, actual.rate)
        self.assertEqual('sync', actual.tag)
        self.assertEqual(Absent.get_absent(), actual.body)
        self.assertIsInstance(actual.form, SyncRequestForm)

    def test_sync_request_existing_body(self):
        # Given
        node_uri = 'foo_sync_node'
        lane_uri = 'bar_sync_lane'
        body = Text.create_from('Sync_Body')
        priority = 3.5
        rate = 2.0
        # When
        actual = SyncRequest(node_uri, lane_uri, priority, rate, body=body)
        # Then
        self.assertEqual('foo_sync_node', actual.node_uri)
        self.assertEqual('bar_sync_lane', actual.lane_uri)
        self.assertEqual(3.5, actual.prio)
        self.assertEqual(2.0, actual.rate)
        self.assertEqual('sync', actual.tag)
        self.assertEqual(body, actual.body)
        self.assertIsInstance(actual.form, SyncRequestForm)

    def test_synced_response_empty_body(self):
        # Given
        node_uri = 'foo_synced_node'
        lane_uri = 'bar_synced_lane'
        # When
        actual = SyncedResponse(node_uri, lane_uri)
        # Then
        self.assertEqual('foo_synced_node', actual.node_uri)
        self.assertEqual('bar_synced_lane', actual.lane_uri)
        self.assertEqual('synced', actual.tag)
        self.assertEqual(Absent.get_absent(), actual.body)
        self.assertIsInstance(actual.form, SyncedResponseForm)

    def test_synced_response_existing_body(self):
        # Given
        node_uri = 'foo_synced_node'
        lane_uri = 'bar_synced_lane'
        body = Text.create_from('Synced_Body')
        # When
        actual = SyncedResponse(node_uri, lane_uri, body=body)
        # Then
        self.assertEqual('foo_synced_node', actual.node_uri)
        self.assertEqual('bar_synced_lane', actual.lane_uri)
        self.assertEqual('synced', actual.tag)
        self.assertEqual(body, actual.body)
        self.assertIsInstance(actual.form, SyncedResponseForm)

    def test_linked_response_empty_body(self):
        # Given
        node_uri = 'foo_linked_node'
        lane_uri = 'bar_linked_lane'
        # When
        actual = LinkedResponse(node_uri, lane_uri)
        # Then
        self.assertEqual('foo_linked_node', actual.node_uri)
        self.assertEqual('bar_linked_lane', actual.lane_uri)
        self.assertEqual('linked', actual.tag)
        self.assertEqual(Absent.get_absent(), actual.body)
        self.assertIsInstance(actual.form, LinkedResponseForm)

    def test_linked_response_existing_body(self):
        # Given
        node_uri = 'foo_linked_node'
        lane_uri = 'bar_linked_lane'
        body = Text.create_from('Linked_Body')
        priority = 1.13
        rate = 3.11
        # When
        actual = LinkedResponse(node_uri, lane_uri, priority, rate, body)
        # Then
        self.assertEqual('foo_linked_node', actual.node_uri)
        self.assertEqual('bar_linked_lane', actual.lane_uri)
        self.assertEqual('linked', actual.tag)
        self.assertEqual(body, actual.body)
        self.assertIsInstance(actual.form, LinkedResponseForm)

    def test_command_message_empty_body(self):
        # Given
        node_uri = 'foo_command_node'
        lane_uri = 'bar_command_lane'
        # When
        actual = CommandMessage(node_uri, lane_uri)
        # Then
        self.assertEqual('foo_command_node', actual.node_uri)
        self.assertEqual('bar_command_lane', actual.lane_uri)
        self.assertEqual('command', actual.tag)
        self.assertEqual(Absent.get_absent(), actual.body)
        self.assertIsInstance(actual.form, CommandMessageForm)

    def test_command_message_existing_body(self):
        # Given
        node_uri = 'foo_command_node'
        lane_uri = 'bar_command_lane'
        body = Text.create_from('Command_Body')
        # When
        actual = CommandMessage(node_uri, lane_uri, body)
        # Then
        self.assertEqual('foo_command_node', actual.node_uri)
        self.assertEqual('bar_command_lane', actual.lane_uri)
        self.assertEqual('command', actual.tag)
        self.assertEqual(body, actual.body)
        self.assertIsInstance(actual.form, CommandMessageForm)

    def test_event_message_empty_body(self):
        # Given
        node_uri = 'foo_event_node'
        lane_uri = 'bar_event_lane'
        # When
        actual = EventMessage(node_uri, lane_uri)
        # Then
        self.assertEqual('foo_event_node', actual.node_uri)
        self.assertEqual('bar_event_lane', actual.lane_uri)
        self.assertEqual('event', actual.tag)
        self.assertEqual(Absent.get_absent(), actual.body)
        self.assertIsInstance(actual.form, EventMessageForm)

    def test_event_message_existing_body(self):
        # Given
        node_uri = 'foo_event_node'
        lane_uri = 'bar_event_lane'
        body = Text.create_from('Event_Body')
        # When
        actual = EventMessage(node_uri, lane_uri, body)
        # Then
        self.assertEqual('foo_event_node', actual.node_uri)
        self.assertEqual('bar_event_lane', actual.lane_uri)
        self.assertEqual('event', actual.tag)
        self.assertEqual(body, actual.body)
        self.assertIsInstance(actual.form, EventMessageForm)
