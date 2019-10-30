import asyncio
import unittest
from aiounittest import async_test

from swim.warp.warp import Envelope, SyncRequestForm, SyncedResponseForm, LinkedResponseForm, EventMessageForm, CommandMessageForm


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
