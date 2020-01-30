#  Copyright 2015-2020 SWIM.AI inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
import unittest
from concurrent.futures import Future
from unittest.mock import patch

from aiounittest import async_test

from swimai import SwimClient
from swimai.client.connections import DownlinkManager
from swimai.client.downlinks import EventDownlinkModel, DownlinkModel, ValueDownlinkModel
from swimai.structures import Record, Text, Attr, RecordMap
from swimai.warp import LinkedResponse, SyncedResponse, EventMessage, UnlinkedResponse
from test.utils import MockConnection, MockExecuteOnException


class TestDownlinks(unittest.TestCase):

    @async_test
    async def test_create_event_downlink_model(self):
        # Given
        with SwimClient() as client:
            # When
            actual = EventDownlinkModel(client)
            pass
            # Then
            self.assertIsInstance(actual, EventDownlinkModel)
            self.assertIsInstance(actual, DownlinkModel)
            self.assertEqual(client, actual.client)
            self.assertFalse(actual.linked.is_set())

    @async_test
    async def test_open_downlink(self):
        # Given
        with SwimClient() as client:
            downlink = EventDownlinkModel(client)
            downlink.connection = MockConnection().get_mock_connection()
            # When
            actual = downlink.open()
            # Then
            self.assertEqual(downlink, actual)
            self.assertIsInstance(actual.task, Future)
            self.assertFalse(actual.task.done())

    @async_test
    async def test_close_downlink(self):
        # Given
        with SwimClient() as client:
            downlink = EventDownlinkModel(client)
            downlink.connection = MockConnection().get_mock_connection()
            downlink = downlink.open()

            # When
            actual = downlink.close()
            while not actual.task.done():
                pass

            # Then
            self.assertEqual(downlink, actual)
            self.assertIsInstance(actual.task, Future)
            self.assertTrue(actual.task.done())
            self.assertTrue(actual.task.cancelled())

    @async_test
    async def test_downlink_receive_message_linked(self):
        # Given
        with SwimClient() as client:
            downlink = EventDownlinkModel(client)
            downlink.connection = MockConnection().get_mock_connection()
            downlink.connection.owner = downlink
            linked_message = LinkedResponse('linked_node', 'linked_lane')
            downlink.connection.messages_to_receive.append(linked_message)

            # When
            actual = downlink.open()
            while not actual.linked.is_set():
                pass

            # Then
            self.assertEqual(downlink, actual)
            self.assertTrue(actual.linked.is_set())

    @async_test
    async def test_downlink_receive_message_synced(self):
        # Given
        with SwimClient() as client:
            downlink = ValueDownlinkModel(client)
            downlink.connection = MockConnection().get_mock_connection()
            downlink.connection.owner = downlink
            synced_message = SyncedResponse('synced_node', 'synced_lane')
            downlink.connection.messages_to_receive.append(synced_message)

            # When
            actual = downlink.open()
            while not actual.synced.is_set():
                pass

            # Then
            self.assertEqual(downlink, actual)
            self.assertTrue(actual.synced.is_set())

    @async_test
    async def test_downlink_receive_message_event(self):
        # Given
        with SwimClient(terminate_on_exception=True) as client:
            downlink = ValueDownlinkModel(client)
            downlink.connection = MockConnection().get_mock_connection()
            downlink.connection.owner = downlink
            downlink_manager = DownlinkManager(downlink.connection)
            downlink.downlink_manager = downlink_manager
            event_message = EventMessage('event_node', 'event_lane',
                                         Record.create_from(Text.create_from('event_body')))
            downlink.connection.messages_to_receive.append(event_message)

            # When
            actual = downlink.open()
            while not actual.value:
                pass

            # Then
            self.assertEqual(downlink, actual)
            self.assertEqual('event_body', actual.value.value)

    @patch('warnings.warn')
    @async_test
    async def test_downlink_receive_message_unlinked(self, mock_warn):
        # Given
        with SwimClient(execute_on_exception=MockExecuteOnException.get_mock_execute_on_exception()) as client:
            downlink = EventDownlinkModel(client)
            downlink.connection = MockConnection().get_mock_connection()
            downlink.connection.owner = downlink

            body = RecordMap.create()
            body.add(Attr.create_attr('laneNotFound', 'foo'))

            unlinked_message = UnlinkedResponse('unlinked_node', 'unlinked_lane', body=body)
            downlink.connection.messages_to_receive.append(unlinked_message)

            # When
            actual = downlink.open()
            while not MockExecuteOnException.get_mock_execute_on_exception().called:
                pass

            # Then
            self.assertEqual(downlink, actual)
            self.assertEqual('Lane "None" was not found on the remote agent!', mock_warn.call_args_list[0][0][0])
