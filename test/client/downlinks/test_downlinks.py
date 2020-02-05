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
import inspect
import unittest
from collections import Callable
from concurrent.futures import Future
from unittest.mock import patch

from aiounittest import async_test

from swimai import SwimClient
from swimai.client.connections import DownlinkManager, DownlinkManagerStatus
from swimai.client.downlinks import EventDownlinkModel, DownlinkModel, ValueDownlinkModel, EventDownlinkView, \
    DownlinkView, ValueDownlinkView
from swimai.structures import Record, Text, Attr, RecordMap, Absent, Num, Bool, Slot, Value
from swimai.warp import LinkedResponse, SyncedResponse, EventMessage, UnlinkedResponse
from test.utils import MockConnection, MockExecuteOnException, MockWebsocketConnect, MockWebsocket, \
    mock_did_set_confirmation, ReceiveLoop, MockPerson, MockPet, NewScope, MockNoDefaultConstructor, MockCar, \
    mock_func, mock_coro, MockModel, MockDownlinkManager, mock_on_event_callback, MockEventCallback, MockDidSetCallback


class TestDownlinks(unittest.TestCase):

    # TODO create one for map downlinks
    @async_test
    async def test_create_event_downlink_model(self):
        # Given
        with SwimClient() as client:
            # When
            actual = EventDownlinkModel(client)

        # Then
        self.assertIsInstance(actual, EventDownlinkModel)
        self.assertIsInstance(actual, DownlinkModel)
        self.assertEqual(client, actual.client)
        self.assertFalse(actual.linked.is_set())

    @async_test
    async def test_open_downlink_model(self):
        # Given
        with SwimClient() as client:
            downlink = EventDownlinkModel(client)
            downlink.connection = MockConnection.get_mock_connection()
            # When
            actual = downlink.open()

            # Then
            self.assertFalse(actual.task.done())

        self.assertTrue(actual.task.done())
        self.assertEqual(downlink, actual)
        self.assertIsInstance(actual.task, Future)

    @async_test
    async def test_close_downlink_model(self):
        # Given
        with SwimClient() as client:
            downlink = EventDownlinkModel(client)
            downlink.connection = MockConnection.get_mock_connection()
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
    async def test_downlink_model_receive_message_linked(self):
        # Given
        with SwimClient() as client:
            downlink = EventDownlinkModel(client)
            downlink.connection = MockConnection.get_mock_connection()
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
    async def test_downlink_model_receive_message_synced(self):
        # Given
        with SwimClient() as client:
            downlink = ValueDownlinkModel(client)
            downlink.connection = MockConnection.get_mock_connection()
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
    async def test_downlink_model_receive_message_event(self):
        # Given
        with SwimClient() as client:
            downlink = ValueDownlinkModel(client)
            downlink.connection = MockConnection.get_mock_connection()
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
        self.assertEqual('event_body', actual.value)

    @patch('warnings.warn')
    @async_test
    async def test_downlink_model_receive_message_unlinked(self, mock_warn):
        # Given
        with SwimClient(execute_on_exception=MockExecuteOnException.get_mock_execute_on_exception()) as client:
            downlink = EventDownlinkModel(client)
            downlink.connection = MockConnection.get_mock_connection()
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

    # TODO create one for map downlinks
    @async_test
    async def test_create_event_downlink_view(self):
        # Given
        with SwimClient() as client:
            # When
            actual = EventDownlinkView(client)

        # Then
        self.assertIsInstance(actual, EventDownlinkView)
        self.assertIsInstance(actual, DownlinkView)
        self.assertEqual(client, actual.client)
        self.assertFalse(actual.is_open)
        self.assertFalse(actual.strict)

    @async_test
    async def test_downlink_view_set_host_uri_ws(self):
        # Given
        with SwimClient() as client:
            downlink = EventDownlinkView(client)
            host_uri = 'ws://127.0.0.1'
            # When
            actual = downlink.set_host_uri(host_uri)

        # Then
        self.assertEqual(downlink, actual)
        self.assertEqual(host_uri, actual.host_uri)

    @async_test
    async def test_downlink_view_set_host_uri_warp(self):
        # Given
        with SwimClient() as client:
            downlink = EventDownlinkView(client)
            host_uri = 'warp://127.0.0.1'
            # When
            actual = downlink.set_host_uri(host_uri)

        # Then
        self.assertEqual(downlink, actual)
        self.assertEqual('ws://127.0.0.1', actual.host_uri)

    @async_test
    async def test_downlink_view_set_node_uri(self):
        # Given
        with SwimClient() as client:
            downlink = EventDownlinkView(client)
            node_uri = 'boo/bar'
            # When
            actual = downlink.set_node_uri(node_uri)

        # Then
        self.assertEqual(downlink, actual)
        self.assertEqual(node_uri, actual.node_uri)

    @async_test
    async def test_downlink_view_set_lane_uri(self):
        # Given
        with SwimClient() as client:
            downlink = EventDownlinkView(client)
            lane_uri = 'shop'
            # When
            actual = downlink.set_lane_uri(lane_uri)

        # Then
        self.assertEqual(downlink, actual)
        self.assertEqual(lane_uri, actual.lane_uri)

    @async_test
    async def test_downlink_view_route(self):
        # Given
        with SwimClient() as client:
            downlink = EventDownlinkView(client)
            node_uri = 'boo/bar'
            lane_uri = 'shop'
            downlink.set_node_uri(node_uri)
            downlink.set_lane_uri(lane_uri)
            # When
            actual = downlink.route

        # Then
        self.assertEqual(f'{node_uri}/{lane_uri}', actual)

    @patch('websockets.connect', new_callable=MockWebsocketConnect)
    @async_test
    async def test_downlink_view_open(self, mock_websocket_connect):
        # Given
        message = '@event(node:"boo/bar",lane:shop)'
        MockWebsocket.get_mock_websocket().messages_to_send.append(message)
        loop_class = ReceiveLoop()
        MockWebsocket.get_mock_websocket().custom_recv_func = loop_class.recv_loop
        with SwimClient() as client:
            downlink = ValueDownlinkView(client)
            downlink.set_host_uri('ws://127.0.0.1')
            downlink.set_node_uri('boo/bar')
            downlink.set_lane_uri('shop')
            downlink.did_set(mock_did_set_confirmation)
            # When
            actual = downlink.open()

            while loop_class.call_count == 0:
                pass

            # Then
            self.assertTrue(actual.is_open)

        self.assertFalse(actual.is_open)
        self.assertTrue(mock_websocket_connect.called)
        self.assertIsInstance(actual.model, DownlinkModel)

    @patch('websockets.connect', new_callable=MockWebsocketConnect)
    @async_test
    async def test_downlink_view_close(self, mock_websocket_connect):
        # Given
        message = '@event(node:"boo/bar",lane:shop)'
        MockWebsocket.get_mock_websocket().messages_to_send.append(message)
        loop_class = ReceiveLoop()
        MockWebsocket.get_mock_websocket().custom_recv_func = loop_class.recv_loop
        with SwimClient() as client:
            downlink = ValueDownlinkView(client)
            downlink.set_host_uri('ws://127.0.0.1')
            downlink.set_node_uri('boo/bar')
            downlink.set_lane_uri('shop')
            downlink.did_set(mock_did_set_confirmation)
            downlink.open()
            while loop_class.call_count == 0:
                pass
            # When
            actual = downlink.close()

        # Then
        self.assertFalse(actual.is_open)
        self.assertTrue(mock_websocket_connect.called)
        self.assertIsInstance(actual.model, DownlinkModel)

    @async_test
    async def test_downlink_view_get_registered_classes_from_self(self):
        # Given
        with SwimClient() as client:
            downlink = ValueDownlinkView(client)
            # When
            mock_person_class = MockPerson
            downlink.register_class(mock_person_class)

        # Then
        self.assertEqual(1, len(downlink.registered_classes))
        self.assertEqual(mock_person_class, downlink.registered_classes.get('MockPerson'))

    @patch('websockets.connect', new_callable=MockWebsocketConnect)
    @async_test
    async def test_downlink_view_get_registered_classes_from_manager(self, mock_websocket_connect):
        # Given
        message = '@event(node:"boo/bar",lane:shop)'
        MockWebsocket.get_mock_websocket().messages_to_send.append(message)
        loop_class = ReceiveLoop()
        MockWebsocket.get_mock_websocket().custom_recv_func = loop_class.recv_loop

        with SwimClient() as client:
            downlink = ValueDownlinkView(client)
            downlink.set_host_uri('ws://127.0.0.1')
            downlink.set_node_uri('boo/bar')
            downlink.set_lane_uri('shop')
            downlink.did_set(mock_did_set_confirmation)

            # When
            mock_person_class = MockPerson
            downlink.register_class(mock_person_class)
            downlink.open()
            while loop_class.call_count == 0:
                pass

        # Then
        self.assertEqual(1, len(downlink.registered_classes))
        self.assertTrue(mock_websocket_connect.called)
        self.assertEqual(mock_person_class, downlink.registered_classes.get('MockPerson'))

    @async_test
    async def test_downlink_view_get_strict_from_self(self):
        # Given
        with SwimClient() as client:
            # When
            downlink = ValueDownlinkView(client)

        # Then
        self.assertFalse(downlink.strict)

    @patch('websockets.connect', new_callable=MockWebsocketConnect)
    @async_test
    async def test_downlink_view_get_strict_from_manager(self, mock_websocket_connect):
        # Given
        message = '@event(node:"boo/bar",lane:shop)'
        MockWebsocket.get_mock_websocket().messages_to_send.append(message)
        loop_class = ReceiveLoop()
        MockWebsocket.get_mock_websocket().custom_recv_func = loop_class.recv_loop

        with SwimClient() as client:
            downlink = ValueDownlinkView(client)
            downlink.set_host_uri('ws://127.0.0.1')
            downlink.set_node_uri('boo/bar')
            downlink.set_lane_uri('shop')
            downlink.did_set(mock_did_set_confirmation)

            # When
            downlink.open()
            while loop_class.call_count == 0:
                pass

        # Then
        self.assertFalse(downlink.strict)
        self.assertTrue(mock_websocket_connect.called)

    @async_test
    async def test_downlink_view_set_strict_to_self(self):
        # Given
        with SwimClient() as client:
            downlink = ValueDownlinkView(client)
            # When
            downlink.strict = True

        # Then
        self.assertTrue(downlink.strict)

    @patch('websockets.connect', new_callable=MockWebsocketConnect)
    @async_test
    async def test_downlink_view_set_strict_to_manager(self, mock_websocket_connect):
        # Given
        message = '@event(node:"boo/bar",lane:shop)'
        MockWebsocket.get_mock_websocket().messages_to_send.append(message)
        loop_class = ReceiveLoop()
        MockWebsocket.get_mock_websocket().custom_recv_func = loop_class.recv_loop

        with SwimClient() as client:
            downlink = ValueDownlinkView(client)
            downlink.set_host_uri('ws://127.0.0.1')
            downlink.set_node_uri('boo/bar')
            downlink.set_lane_uri('shop')
            downlink.did_set(mock_did_set_confirmation)
            downlink.open()
            while loop_class.call_count == 0:
                pass

            # When
            downlink.strict = True

        # Then
        self.assertTrue(downlink.strict)
        self.assertTrue(mock_websocket_connect.called)

    @async_test
    async def test_downlink_view_register_classes(self):
        # Given
        with SwimClient() as client:
            downlink = ValueDownlinkView(client)
            # When
            mock_person_class = MockPerson
            mock_pet_class = MockPet
            downlink.register_classes([mock_person_class, mock_pet_class])

        # Then
        self.assertEqual(2, len(downlink.registered_classes))
        self.assertEqual(mock_person_class, downlink.registered_classes.get('MockPerson'))
        self.assertEqual(mock_pet_class, downlink.registered_classes.get('MockPet'))

    @async_test
    async def test_downlink_view_register_class_self(self):
        # Given
        with SwimClient() as client:
            downlink = ValueDownlinkView(client)
            # When
            mock_pet_class = MockPet
            downlink.register_class(mock_pet_class)

        # Then
        self.assertEqual(1, len(downlink.registered_classes))
        self.assertEqual(mock_pet_class, downlink.registered_classes.get('MockPet'))

    @async_test
    async def test_downlink_view_register_deregistered_class_self(self):
        # Given
        with SwimClient() as client:
            downlink = ValueDownlinkView(client)
            # When
            mock_pet_class = MockPet
            downlink.register_class(mock_pet_class)
            self.assertEqual(1, len(downlink.registered_classes))
            downlink.deregister_class(mock_pet_class)
            self.assertEqual(0, len(downlink.registered_classes))
            downlink.register_class(mock_pet_class)

        # Then
        self.assertEqual(1, len(downlink.registered_classes))
        self.assertEqual(mock_pet_class, downlink.registered_classes.get('MockPet'))

    @async_test
    async def test_downlink_view_overwrite_register_class_self(self):
        # Given
        with SwimClient() as client:
            downlink = ValueDownlinkView(client)
            # When
            mock_person_class = MockPerson
            mock_second_person_class = NewScope.MockPerson
            downlink.register_class(mock_person_class)
            downlink.register_class(mock_second_person_class)

        # Then
        self.assertEqual(1, len(downlink.registered_classes))
        self.assertEqual(mock_second_person_class, downlink.registered_classes.get('MockPerson'))

    @patch('websockets.connect', new_callable=MockWebsocketConnect)
    @async_test
    async def test_downlink_view_register_class_downlink_manager(self, mock_websocket_connect):
        # Given
        message = '@event(node:"boo/bar",lane:shop)'
        MockWebsocket.get_mock_websocket().messages_to_send.append(message)
        loop_class = ReceiveLoop()
        MockWebsocket.get_mock_websocket().custom_recv_func = loop_class.recv_loop

        with SwimClient() as client:
            downlink = ValueDownlinkView(client)
            downlink.set_host_uri('ws://127.0.0.1')
            downlink.set_node_uri('boo/bar')
            downlink.set_lane_uri('shop')
            downlink.did_set(mock_did_set_confirmation)
            downlink.open()
            while loop_class.call_count == 0:
                pass
            # When
            mock_person_class = MockPerson
            downlink.register_class(mock_person_class)

        # Then
        self.assertEqual(1, len(downlink.registered_classes))
        self.assertTrue(mock_websocket_connect.called)
        self.assertEqual(mock_person_class, downlink.registered_classes.get('MockPerson'))

    @patch('websockets.connect', new_callable=MockWebsocketConnect)
    @async_test
    async def test_downlink_view_overwrite_register_class_downlink_manager(self, mock_websocket_connect):
        # Given
        message = '@event(node:"boo/bar",lane:shop)'
        MockWebsocket.get_mock_websocket().messages_to_send.append(message)
        loop_class = ReceiveLoop()
        MockWebsocket.get_mock_websocket().custom_recv_func = loop_class.recv_loop

        with SwimClient() as client:
            downlink = ValueDownlinkView(client)
            downlink.set_host_uri('ws://127.0.0.1')
            downlink.set_node_uri('boo/bar')
            downlink.set_lane_uri('shop')
            downlink.did_set(mock_did_set_confirmation)
            downlink.open()
            while loop_class.call_count == 0:
                pass
            # When
            mock_person_class = MockPerson
            downlink.register_class(mock_person_class)
            mock_second_person_class = NewScope.MockPerson
            downlink.register_class(mock_second_person_class)

        # Then
        self.assertEqual(1, len(downlink.registered_classes))
        self.assertTrue(mock_websocket_connect.called)
        self.assertEqual(mock_second_person_class, downlink.registered_classes.get('MockPerson'))

    @patch('warnings.warn')
    @async_test
    async def test_downlink_view_register_class_exception_no_default_constructor(self, mock_warn):
        # Given
        with SwimClient() as client:
            downlink = ValueDownlinkView(client)
            # When
            mock_no_default_constructor = MockNoDefaultConstructor
            downlink.register_class(mock_no_default_constructor)

        # Then
        self.assertEqual(
            'Class "MockNoDefaultConstructor" must have a default constructor or default values for all arguments!',
            mock_warn.mock_calls[0][1][0])
        self.assertEqual(0, len(downlink.registered_classes))

    @async_test
    async def test_downlink_view_deregister_all_classes_self(self):
        # Given
        with SwimClient() as client:
            downlink = ValueDownlinkView(client)
            mock_person_class = MockPerson
            mock_pet_class = MockPet
            mock_car_class = MockCar
            downlink.register_class(mock_person_class)
            downlink.register_class(mock_pet_class)
            downlink.register_class(mock_car_class)
            self.assertTrue(3, len(downlink.registered_classes))
            # When
            downlink.deregister_all_classes()

        # Then
        self.assertEqual(0, len(downlink.registered_classes))

    @patch('websockets.connect', new_callable=MockWebsocketConnect)
    @async_test
    async def test_downlink_view_deregister_all_classes_manager(self, mock_websocket_connect):
        # Given
        message = '@event(node:"boo/bar",lane:shop)'
        MockWebsocket.get_mock_websocket().messages_to_send.append(message)
        loop_class = ReceiveLoop()
        MockWebsocket.get_mock_websocket().custom_recv_func = loop_class.recv_loop

        with SwimClient() as client:
            downlink = ValueDownlinkView(client)
            downlink.set_host_uri('ws://127.0.0.1')
            downlink.set_node_uri('boo/bar')
            downlink.set_lane_uri('shop')
            downlink.did_set(mock_did_set_confirmation)
            downlink.open()
            while loop_class.call_count == 0:
                pass
            mock_person_class = MockPerson
            mock_pet_class = MockPet
            mock_car_class = MockCar
            downlink.register_class(mock_person_class)
            downlink.register_class(mock_pet_class)
            downlink.register_class(mock_car_class)
            self.assertTrue(3, len(downlink.registered_classes))
            # When
            downlink.deregister_all_classes()

        # Then
        self.assertEqual(0, len(downlink.registered_classes))
        self.assertTrue(mock_websocket_connect.called)

    @async_test
    async def test_downlink_view_deregister_classes(self):
        # Given
        with SwimClient() as client:
            downlink = ValueDownlinkView(client)
            mock_person_class = MockPerson
            mock_pet_class = MockPet
            mock_car_class = MockCar
            downlink.register_class(mock_person_class)
            downlink.register_class(mock_pet_class)
            downlink.register_class(mock_car_class)
            self.assertTrue(3, len(downlink.registered_classes))
            # When
            downlink.deregister_classes([mock_pet_class, mock_person_class])

        # Then
        self.assertEqual(1, len(downlink.registered_classes))
        self.assertEqual(mock_car_class, downlink.registered_classes.get('MockCar'))

    @async_test
    async def test_downlink_view_deregister_class_self(self):
        # Given
        with SwimClient() as client:
            downlink = ValueDownlinkView(client)
            mock_person_class = MockPerson
            mock_pet_class = MockPet
            mock_car_class = MockCar
            downlink.register_class(mock_person_class)
            downlink.register_class(mock_pet_class)
            downlink.register_class(mock_car_class)
            self.assertTrue(3, len(downlink.registered_classes))
            self.assertEqual(mock_car_class, downlink.registered_classes.get('MockCar'))
            self.assertEqual(mock_pet_class, downlink.registered_classes.get('MockPet'))
            self.assertEqual(mock_person_class, downlink.registered_classes.get('MockPerson'))
            # When
            downlink.deregister_class(mock_car_class)

        # Then
        self.assertEqual(2, len(downlink.registered_classes))
        self.assertEqual(mock_pet_class, downlink.registered_classes.get('MockPet'))
        self.assertEqual(mock_person_class, downlink.registered_classes.get('MockPerson'))

    @async_test
    async def test_downlink_view_deregister_class_self_missing(self):
        # Given
        with SwimClient() as client:
            downlink = ValueDownlinkView(client)
            mock_person_class = MockPerson
            mock_pet_class = MockPet
            mock_car_class = MockCar
            downlink.register_class(mock_person_class)
            downlink.register_class(mock_pet_class)
            self.assertTrue(2, len(downlink.registered_classes))
            self.assertEqual(mock_person_class, downlink.registered_classes.get('MockPerson'))
            self.assertEqual(mock_pet_class, downlink.registered_classes.get('MockPet'))
            # When
            downlink.deregister_class(mock_car_class)

        # Then
        self.assertEqual(2, len(downlink.registered_classes))
        self.assertEqual(mock_person_class, downlink.registered_classes.get('MockPerson'))
        self.assertEqual(mock_pet_class, downlink.registered_classes.get('MockPet'))

    @patch('websockets.connect', new_callable=MockWebsocketConnect)
    @async_test
    async def test_downlink_view_deregister_class_manager(self, mock_websocket_connect):
        # Given
        message = '@event(node:"boo/bar",lane:shop)'
        MockWebsocket.get_mock_websocket().messages_to_send.append(message)
        loop_class = ReceiveLoop()
        MockWebsocket.get_mock_websocket().custom_recv_func = loop_class.recv_loop

        with SwimClient() as client:
            downlink = ValueDownlinkView(client)
            downlink.set_host_uri('ws://127.0.0.1')
            downlink.set_node_uri('boo/bar')
            downlink.set_lane_uri('shop')
            downlink.did_set(mock_did_set_confirmation)
            downlink.open()
            while loop_class.call_count == 0:
                pass
            mock_person_class = MockPerson
            mock_pet_class = MockPet
            mock_car_class = MockCar
            downlink.register_class(mock_person_class)
            downlink.register_class(mock_pet_class)
            downlink.register_class(mock_car_class)
            self.assertTrue(3, len(downlink.registered_classes))
            # When
            downlink.deregister_class(mock_car_class)

        # Then
        self.assertEqual(2, len(downlink.registered_classes))
        self.assertTrue(mock_websocket_connect.called)
        self.assertEqual(mock_person_class, downlink.registered_classes.get('MockPerson'))
        self.assertEqual(mock_pet_class, downlink.registered_classes.get('MockPet'))

    @patch('websockets.connect', new_callable=MockWebsocketConnect)
    @async_test
    async def test_downlink_view_deregister_class_manager_missing(self, mock_websocket_connect):
        # Given
        message = '@event(node:"boo/bar",lane:shop)'
        MockWebsocket.get_mock_websocket().messages_to_send.append(message)
        loop_class = ReceiveLoop()
        MockWebsocket.get_mock_websocket().custom_recv_func = loop_class.recv_loop

        with SwimClient() as client:
            downlink = ValueDownlinkView(client)
            downlink.set_host_uri('ws://127.0.0.1')
            downlink.set_node_uri('boo/bar')
            downlink.set_lane_uri('shop')
            downlink.did_set(mock_did_set_confirmation)
            downlink.open()
            while loop_class.call_count == 0:
                pass
            mock_person_class = MockPerson
            mock_pet_class = MockPet
            mock_car_class = MockCar
            downlink.register_class(mock_person_class)
            downlink.register_class(mock_pet_class)
            self.assertTrue(2, len(downlink.registered_classes))
            # When
            downlink.deregister_class(mock_car_class)

        # Then
        self.assertEqual(2, len(downlink.registered_classes))
        self.assertTrue(mock_websocket_connect.called)
        self.assertEqual(mock_person_class, downlink.registered_classes.get('MockPerson'))
        self.assertEqual(mock_pet_class, downlink.registered_classes.get('MockPet'))

    @async_test
    async def test_downlink_view_validate_callback_function(self):
        # Given
        func = mock_func
        # When
        actual = DownlinkView.validate_callback(func)
        result = await actual()
        # Then
        self.assertEqual('mock_func_response', result)
        self.assertTrue(isinstance(actual, Callable))
        self.assertTrue(inspect.iscoroutinefunction(actual))

    @async_test
    async def test_downlink_view_validate_coro(self):
        # Given
        coro = mock_coro
        # When
        actual = DownlinkView.validate_callback(coro)
        result = await actual()
        # Then
        self.assertEqual('mock_coro_response', result)
        self.assertTrue(isinstance(actual, Callable))
        self.assertTrue(inspect.iscoroutinefunction(actual))

    @async_test
    async def test_downlink_view_validate_invalid(self):
        # Given
        integer = 31
        # When
        with self.assertRaises(TypeError) as error:
            # noinspection PyTypeChecker
            DownlinkView.validate_callback(integer)

        # Then
        message = error.exception.args[0]
        self.assertEqual(message, 'Callback must be a coroutine or a function!')

    @async_test
    async def test_downlink_view_assign_manager(self):
        # Given
        connection = MockWebsocketConnect()
        with SwimClient() as client:
            downlink = ValueDownlinkView(client)
            downlink.strict = True
            mock_person_class = MockPerson
            mock_car_class = MockCar
            downlink.register_class(mock_person_class)
            downlink.register_class(mock_car_class)
            manager = DownlinkManager(connection)
            manager.downlink_model = MockModel()
            # When
            await downlink.assign_manager(manager)

        # Then
        self.assertEqual(manager.downlink_model, downlink.model)
        self.assertEqual(manager.registered_classes, downlink.registered_classes)
        self.assertEqual(manager.strict, downlink.strict)
        self.assertEqual(manager, downlink.downlink_manager)
        self.assertTrue(manager.strict)
        self.assertIsInstance(manager.downlink_model, MockModel)
        self.assertEqual(2, len(manager.registered_classes))
        self.assertEqual(mock_person_class, manager.registered_classes.get('MockPerson'))
        self.assertEqual(mock_car_class, manager.registered_classes.get('MockCar'))

    @async_test
    async def test_downlink_view_initialise_model(self):
        # Given
        connection = MockWebsocketConnect()
        manager = DownlinkManager(connection)
        with SwimClient() as client:
            model = ValueDownlinkModel(client)
            downlink = ValueDownlinkView(client)
            downlink.strict = True
            mock_person_class = MockPerson
            mock_car_class = MockCar
            downlink.register_class(mock_person_class)
            downlink.register_class(mock_car_class)
            host_uri = 'ws://host_uri'
            lane_uri = 'lane/uri'
            node_uri = 'node_uri'
            downlink.set_host_uri(host_uri)
            downlink.set_lane_uri(lane_uri)
            downlink.set_node_uri(node_uri)
            # When
            await downlink.initalise_model(manager, model)

        # Then
        self.assertEqual(downlink.registered_classes, manager.registered_classes)
        self.assertEqual(downlink.strict, manager.strict)
        self.assertEqual(manager, model.downlink_manager)
        self.assertEqual(host_uri, model.host_uri)
        self.assertEqual(node_uri, model.node_uri)
        self.assertEqual(lane_uri, model.lane_uri)
        self.assertTrue(manager.strict)
        self.assertEqual(mock_person_class, manager.registered_classes.get('MockPerson'))
        self.assertEqual(mock_car_class, manager.registered_classes.get('MockCar'))

    @patch('websockets.connect', new_callable=MockWebsocketConnect)
    @async_test
    async def test_downlink_view_register_and_deregister_classes(self, mock_websocket_connect):
        # Given
        message = '@event(node:"boo/bar",lane:shop)'
        MockWebsocket.get_mock_websocket().messages_to_send.append(message)
        loop_class = ReceiveLoop()
        MockWebsocket.get_mock_websocket().custom_recv_func = loop_class.recv_loop

        mock_person_class = MockPerson
        mock_pet_class = MockPet
        mock_car_class = MockCar

        with SwimClient() as client:
            downlink = ValueDownlinkView(client)
            downlink.set_host_uri('ws://127.0.0.1')
            downlink.set_node_uri('boo/bar')
            downlink.set_lane_uri('shop')
            downlink.did_set(mock_did_set_confirmation)
            downlink.register_class(mock_person_class)
            downlink.register_class(mock_pet_class)
            downlink.register_class(mock_car_class)
            downlink.open()

            while loop_class.call_count == 0:
                pass
            self.assertTrue(3, len(downlink.registered_classes))
            # When
            second_downlink = ValueDownlinkView(client)
            second_downlink.set_host_uri('ws://127.0.0.1')
            second_downlink.set_node_uri('boo/bar')
            second_downlink.set_lane_uri('shop')
            second_downlink.deregister_class(mock_pet_class)
            second_downlink.open()
            self.assertTrue(2, len(downlink.registered_classes))
            second_downlink.deregister_class(mock_car_class)

        # Then
        self.assertEqual(1, len(downlink.registered_classes))
        self.assertEqual(1, len(second_downlink.registered_classes))
        self.assertTrue(mock_websocket_connect.called)
        self.assertEqual(mock_person_class, downlink.registered_classes.get('MockPerson'))
        self.assertEqual(mock_person_class, second_downlink.registered_classes.get('MockPerson'))

    @async_test
    async def test_event_downlink_model_establish_downlink(self):

        # Given
        with SwimClient() as client:
            downlink_model = EventDownlinkModel(client)
            downlink_model.node_uri = 'foo'
            downlink_model.lane_uri = 'bar'
            downlink_model.connection = MockConnection()

            # When
            await downlink_model.establish_downlink()

        # Then
        self.assertEqual(1, len(downlink_model.connection.messages_sent))
        self.assertEqual('@link(node:foo,lane:bar)', downlink_model.connection.messages_sent[0])

    @async_test
    async def test_event_downlink_model_received_synced(self):
        # Given
        client = SwimClient()
        downlink_model = EventDownlinkModel(client)
        # When
        with self.assertRaises(TypeError) as error:
            await downlink_model.receive_synced()

        # Then
        message = error.exception.args[0]
        self.assertEqual(message, 'Event downlink does not support synced responses!')

    @async_test
    async def test_event_downlink_receive_event_absent(self):
        # Given
        client = SwimClient()
        downlink_model = EventDownlinkModel(client)
        # noinspection PyTypeChecker
        mock_manager = MockDownlinkManager()
        downlink_model.downlink_manager = mock_manager
        event_message = EventMessage(node_uri='foo', lane_uri='bar')
        # When
        await downlink_model.receive_event(event_message)
        # Then
        self.assertEqual(1, mock_manager.called)
        self.assertIsInstance(mock_manager.event, Absent)

    @async_test
    async def test_event_downlink_receive_event_text(self):
        # Given
        client = SwimClient()
        downlink_model = EventDownlinkModel(client)
        # noinspection PyTypeChecker
        mock_manager = MockDownlinkManager()
        downlink_model.downlink_manager = mock_manager
        event_message = EventMessage(node_uri='foo', lane_uri='bar', body=Text.create_from('message'))
        # When
        await downlink_model.receive_event(event_message)
        # Then
        self.assertEqual(1, mock_manager.called)
        self.assertEqual('message', mock_manager.event)

    @async_test
    async def test_event_downlink_receive_event_num(self):
        # Given
        client = SwimClient()
        downlink_model = EventDownlinkModel(client)
        # noinspection PyTypeChecker
        mock_manager = MockDownlinkManager()
        downlink_model.downlink_manager = mock_manager
        event_message = EventMessage(node_uri='foo', lane_uri='bar', body=Num.create_from(21))
        # When
        await downlink_model.receive_event(event_message)
        # Then
        self.assertEqual(1, mock_manager.called)
        self.assertEqual(21, mock_manager.event)

    @async_test
    async def test_event_downlink_receive_event_bool(self):
        # Given
        client = SwimClient()
        downlink_model = EventDownlinkModel(client)
        # noinspection PyTypeChecker
        mock_manager = MockDownlinkManager()
        downlink_model.downlink_manager = mock_manager
        event_message = EventMessage(node_uri='foo', lane_uri='bar', body=Bool.create_from(True))
        # When
        await downlink_model.receive_event(event_message)
        # Then
        self.assertEqual(1, mock_manager.called)
        self.assertEqual(True, mock_manager.event)

    @async_test
    async def test_event_downlink_receive_event_object(self):
        # Given
        client = SwimClient()
        downlink_model = EventDownlinkModel(client)
        # noinspection PyTypeChecker
        mock_manager = MockDownlinkManager()
        downlink_model.downlink_manager = mock_manager
        recon_person = RecordMap.create()
        recon_person.add(Attr.create_attr('MockPerson', Value.extant()))
        recon_person.add(Slot.create_slot(Text.create_from('name'), Text.create_from('George')))
        recon_person.add(Slot.create_slot(Text.create_from('age'), Num.create_from(25)))
        event_message = EventMessage(node_uri='foo', lane_uri='bar', body=recon_person)
        # When
        await downlink_model.receive_event(event_message)
        # Then
        self.assertEqual(1, mock_manager.called)
        self.assertEqual(25, mock_manager.event.age)
        self.assertEqual('George', mock_manager.event.name)

    @async_test
    async def test_event_downlink_view_register_manager(self):
        # Given
        client = SwimClient()
        downlink_view = EventDownlinkView(client)
        downlink_model = EventDownlinkModel(client)
        connection = MockConnection()
        # noinspection PyTypeChecker
        manager = DownlinkManager(connection)
        manager.downlink_model = downlink_model
        # When
        await downlink_view.register_manager(manager)
        # Then
        self.assertEqual(downlink_model, downlink_view.model)
        self.assertEqual(manager, downlink_view.downlink_manager)

    @async_test
    async def test_event_downlink_view_create_downlink_model(self):
        # Given
        client = SwimClient()
        connection = MockConnection()
        # noinspection PyTypeChecker
        manager = DownlinkManager(connection)
        host_uri = 'ws://foo.bar'
        node_uri = 'baz'
        lane_uri = 'qux'
        downlink_view = EventDownlinkView(client)
        downlink_view.set_host_uri(host_uri)
        downlink_view.set_node_uri(node_uri)
        downlink_view.set_lane_uri(lane_uri)
        downlink_view.strict = True
        mock_person_class = MockPerson
        downlink_view.register_class(mock_person_class)
        # When
        actual = await downlink_view.create_downlink_model(manager)
        # Then
        self.assertIsInstance(actual, EventDownlinkModel)
        self.assertEqual(client, actual.client)
        self.assertEqual(downlink_view.strict, actual.downlink_manager.strict)
        self.assertEqual(downlink_view.registered_classes, actual.downlink_manager.registered_classes)
        self.assertEqual(downlink_view.host_uri, actual.host_uri)
        self.assertEqual(downlink_view.node_uri, actual.node_uri)
        self.assertEqual(downlink_view.lane_uri, actual.lane_uri)

    @async_test
    async def test_event_downlink_view_execute_on_event(self):
        # Given
        with SwimClient() as client:
            downlink_view = EventDownlinkView(client)
            mock_on_event = MockEventCallback()
            downlink_view.on_event_callback = mock_on_event.execute
            event = 20
            # When
            await downlink_view.execute_on_event(event)
            while not mock_on_event.called:
                pass

        # Then
        self.assertEqual(20, mock_on_event.event)
        self.assertTrue(mock_on_event.called)

    @async_test
    async def test_event_downlink_view_execute_on_event_missing_callback(self):
        # Given
        with SwimClient() as client:
            downlink_view = EventDownlinkView(client)
            event = 20
            # When
            with patch('swimai.client.swim_client.SwimClient.schedule_task') as mock_schedule_task:
                await downlink_view.execute_on_event(event)

        # Then
        self.assertFalse(mock_schedule_task.called)

    @async_test
    async def test_event_downlink_view_set_on_event(self):
        # Given
        client = SwimClient()
        downlink_view = EventDownlinkView(client)
        # When
        downlink_view.on_event(mock_on_event_callback)
        # Then
        self.assertEqual(mock_on_event_callback, downlink_view.on_event_callback)

    @async_test
    async def test_event_downlink_view_set_on_event_invalid(self):
        # Given
        client = SwimClient()
        downlink_view = EventDownlinkView(client)
        # When
        with self.assertRaises(TypeError) as error:
            # noinspection PyTypeChecker
            downlink_view.on_event(222)
        # Then
        message = error.exception.args[0]
        self.assertEqual(f'Callback must be a coroutine or a function!', message)

    @async_test
    async def test_create_value_downlink_model(self):
        # Given
        with SwimClient() as client:
            # When
            actual = ValueDownlinkModel(client)

        # Then
        self.assertIsInstance(actual, ValueDownlinkModel)
        self.assertIsInstance(actual, DownlinkModel)
        self.assertEqual(client, actual.client)
        self.assertFalse(actual.linked.is_set())
        self.assertFalse(actual.synced.is_set())
        self.assertFalse(actual.value)
        self.assertEqual(actual.value, Value.absent())

    @async_test
    async def test_value_downlink_model_establish_downlink(self):

        # Given
        with SwimClient() as client:
            downlink_model = ValueDownlinkModel(client)
            downlink_model.node_uri = 'foo'
            downlink_model.lane_uri = 'bar'
            downlink_model.connection = MockConnection()

            # When
            await downlink_model.establish_downlink()

        # Then
        self.assertEqual(1, len(downlink_model.connection.messages_sent))
        self.assertEqual('@sync(node:foo,lane:bar)', downlink_model.connection.messages_sent[0])

    @async_test
    async def test_value_downlink_model_receive_synced(self):
        # Given
        with SwimClient() as client:
            downlink_model = ValueDownlinkModel(client)
            # When
            await downlink_model.receive_synced()
        # Then
        self.assertTrue(downlink_model.synced.is_set())

    @async_test
    async def test_value_downlink_model_receive_event_absent(self):
        # Given
        with SwimClient() as client:
            downlink_model = ValueDownlinkModel(client)
            # noinspection PyTypeChecker
            mock_manager = MockDownlinkManager()
            downlink_model.downlink_manager = mock_manager
            # When
            event_message = EventMessage(node_uri='foo', lane_uri='bar')
            await downlink_model.receive_event(event_message)
        # Then
        self.assertEqual(Value.absent(), downlink_model.value)
        self.assertEqual(1, mock_manager.called)
        self.assertEqual(Value.absent(), mock_manager.did_set_new)
        self.assertEqual(Value.absent(), mock_manager.did_set_old)

    @async_test
    async def test_value_downlink_model_receive_event_text(self):
        # Given
        with SwimClient() as client:
            downlink_model = ValueDownlinkModel(client)
            # noinspection PyTypeChecker
            mock_manager = MockDownlinkManager()
            downlink_model.downlink_manager = mock_manager
            # When
            event_message = EventMessage(node_uri='foo', lane_uri='bar', body=Text.create_from('value_text'))
            await downlink_model.receive_event(event_message)
        # Then
        self.assertEqual('value_text', downlink_model.value)
        self.assertEqual(1, mock_manager.called)
        self.assertEqual('value_text', mock_manager.did_set_new)
        self.assertEqual(Value.absent(), mock_manager.did_set_old)

    @async_test
    async def test_value_downlink_model_receive_event_num(self):
        # Given
        with SwimClient() as client:
            downlink_model = ValueDownlinkModel(client)
            # noinspection PyTypeChecker
            mock_manager = MockDownlinkManager()
            downlink_model.downlink_manager = mock_manager
            # When
            event_message = EventMessage(node_uri='foo', lane_uri='bar', body=Num.create_from(11))
            await downlink_model.receive_event(event_message)
            event_message = EventMessage(node_uri='foo', lane_uri='bar', body=Num.create_from(50))
            await downlink_model.receive_event(event_message)
        # Then
        self.assertEqual(50, downlink_model.value)
        self.assertEqual(2, mock_manager.called)
        self.assertEqual(50, mock_manager.did_set_new)
        self.assertEqual(11, mock_manager.did_set_old)

    @async_test
    async def test_value_downlink_model_receive_event_bool(self):
        # Given
        with SwimClient() as client:
            downlink_model = ValueDownlinkModel(client)
            # noinspection PyTypeChecker
            mock_manager = MockDownlinkManager()
            downlink_model.downlink_manager = mock_manager
            # When
            event_message = EventMessage(node_uri='foo', lane_uri='bar', body=Bool.create_from(True))
            await downlink_model.receive_event(event_message)
        # Then
        self.assertEqual(True, downlink_model.value)
        self.assertEqual(1, mock_manager.called)
        self.assertEqual(True, mock_manager.did_set_new)
        self.assertEqual(Value.absent(), mock_manager.did_set_old)

    @async_test
    async def test_value_downlink_model_receive_event_object(self):
        # Given
        with SwimClient() as client:
            downlink_model = ValueDownlinkModel(client)
            # noinspection PyTypeChecker
            mock_manager = MockDownlinkManager()
            downlink_model.downlink_manager = mock_manager
            recon_person = RecordMap.create()
            recon_person.add(Attr.create_attr('MockPerson', Value.extant()))
            recon_person.add(Slot.create_slot(Text.create_from('name'), Text.create_from('Peter')))
            recon_person.add(Slot.create_slot(Text.create_from('age'), Num.create_from(90)))
            event_message = EventMessage(node_uri='foo', lane_uri='bar', body=recon_person)
            # When
            await downlink_model.receive_event(event_message)
        # Then
        self.assertEqual('Peter', downlink_model.value.name)
        self.assertEqual(90, downlink_model.value.age)
        self.assertEqual(1, mock_manager.called)
        self.assertEqual('Peter', mock_manager.did_set_new.name)
        self.assertEqual(90, mock_manager.did_set_new.age)
        self.assertEqual(Value.absent(), mock_manager.did_set_old)

    @async_test
    async def test_value_downlink_model_send_message(self):
        # Given
        with SwimClient() as client:
            downlink_model = ValueDownlinkModel(client)
            downlink_model.connection = MockConnection.get_mock_connection()
            downlink_model.connection.owner = downlink_model
            downlink_model.linked.set()
            recon_person = RecordMap.create()
            recon_person.add(Attr.create_attr('MockPerson', Value.extant()))
            recon_person.add(Slot.create_slot(Text.create_from('name'), Text.create_from('Peter')))
            recon_person.add(Slot.create_slot(Text.create_from('age'), Num.create_from(90)))
            event_message = EventMessage(node_uri='foo', lane_uri='bar', body=recon_person)
            # When
            await downlink_model.send_message(event_message)
        # Then
        self.assertEqual('@event(node:foo,lane:bar)@MockPerson{name:Peter,age:90}',
                         MockConnection.get_mock_connection().messages_sent[0])

    @async_test
    async def test_value_downlink_model_get_value(self):
        # Given
        with SwimClient() as client:
            downlink_model = ValueDownlinkModel(client)
            downlink_model.connection = MockConnection.get_mock_connection()
            downlink_model.connection.owner = downlink_model
            downlink_model.value = 'Test_Value'
            downlink_model.synced.set()
            # When
            actual = await downlink_model.get_value()
        # Then
        self.assertEqual('Test_Value', actual)

    @async_test
    async def test_create_value_downlink_view(self):
        # Given
        with SwimClient() as client:
            # When
            actual = ValueDownlinkView(client)

        # Then
        self.assertIsInstance(actual, ValueDownlinkView)
        self.assertIsInstance(actual, DownlinkView)
        self.assertEqual(client, actual.client)
        self.assertFalse(actual.is_open)
        self.assertFalse(actual.strict)
        self.assertIsNone(actual.did_set_callback)
        self.assertFalse(actual.initialised.is_set())

    @async_test
    async def test_value_downlink_view_register_manager_first_time(self):
        # Given
        with SwimClient() as client:
            downlink_view = ValueDownlinkView(client)
            downlink_model = ValueDownlinkModel(client)
            connection = MockConnection()
            # noinspection PyTypeChecker
            manager = DownlinkManager(connection)
            manager.downlink_model = downlink_model
            # When
            await downlink_view.register_manager(manager)

        # Then
        self.assertTrue(downlink_view.initialised.is_set())
        self.assertEqual(downlink_model, downlink_view.model)
        self.assertEqual(manager, downlink_view.downlink_manager)

    @async_test
    async def test_value_downlink_view_register_manager_already_existing(self):
        # Given
        with SwimClient() as client:
            downlink_view = ValueDownlinkView(client)
            mock_did_set = MockDidSetCallback()
            downlink_view.did_set(mock_did_set.execute)
            downlink_model = ValueDownlinkModel(client)
            downlink_model.value = 'Foo'
            connection = MockConnection()
            # noinspection PyTypeChecker
            manager = DownlinkManager(connection)
            manager.downlink_model = downlink_model
            manager.status = DownlinkManagerStatus.OPEN
            # When
            await downlink_view.register_manager(manager)

            while not mock_did_set.called:
                pass

        # Then
        self.assertTrue(downlink_view.initialised.is_set())
        self.assertEqual(downlink_model, downlink_view.model)
        self.assertEqual(manager, downlink_view.downlink_manager)
        self.assertTrue(mock_did_set.called)
        self.assertEqual('Foo', mock_did_set.new_value)
        self.assertEqual(Value.absent(), mock_did_set.old_value)

    @async_test
    async def test_value_downlink_view_create_downlink_model(self):
        # Given
        with SwimClient() as client:
            downlink_view = ValueDownlinkView(client)
            connection = MockConnection()
            host_uri = 'ws://value.downlink'
            node_uri = 'value'
            lane_uri = 'downlink'
            downlink_view.set_host_uri(host_uri)
            downlink_view.set_node_uri(node_uri)
            downlink_view.set_lane_uri(lane_uri)
            # noinspection PyTypeChecker
            manager = DownlinkManager(connection)
            # When
            actual = await downlink_view.create_downlink_model(manager)

        # Then
        self.assertIsInstance(actual, DownlinkModel)
        self.assertEqual(client, actual.client)
        self.assertEqual(host_uri, actual.host_uri)
        self.assertEqual(node_uri, actual.node_uri)
        self.assertEqual(lane_uri, actual.lane_uri)
        self.assertEqual(manager, actual.downlink_manager)

    @async_test
    async def test_value_downlink_did_set_valid(self):
        # Given
        # When
        # Then
        pass

    @async_test
    async def test_value_downlink_did_set_invalid(self):
        pass

    @async_test
    async def test_value_downlink_value_no_model(self):
        pass

    @async_test
    async def test_value_downlink_value_with_model(self):
        pass
