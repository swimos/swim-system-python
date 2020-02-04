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
import inspect
import unittest
from collections.abc import Callable
from unittest.mock import patch
from aiounittest import async_test

from swimai.client.downlinks import EventDownlinkView
from swimai.client.downlinks.downlink_utils import MapRequest, UpdateRequest, RemoveRequest, convert_to_async
from swimai.structures import RecordMap, Slot, Num, Attr
from test.utils import MockPerson, mock_func


class TestDownlinkUtils(unittest.TestCase):

    @patch('warnings.warn')
    def test_before_open_false(self, mock_warn):
        # Given
        # noinspection PyTypeChecker
        downlink_view = EventDownlinkView(None)
        downlink_view.is_open = False
        # When
        downlink_view.set_node_uri('foo')
        # Then
        self.assertEqual(0, mock_warn.call_count)

    @patch('warnings.warn')
    def test_before_open_true(self, mock_warn):
        # Given
        # noinspection PyTypeChecker
        downlink_view = EventDownlinkView(None)
        downlink_view.is_open = True
        # When
        downlink_view.set_node_uri('foo')
        # Then
        self.assertEqual('Cannot execute "set_node_uri" after the downlink has been open!',
                         mock_warn.mock_calls[0][1][0])

    def test_map_request_get_key_item_primitive(self):
        # Given
        map_request = MapRequest('Foo', 23)
        # When
        actual = map_request.get_key_item()
        # Then
        self.assertIsInstance(actual, RecordMap)
        self.assertIsInstance(actual.get_item(0), Slot)
        self.assertEqual('key', actual.get_item(0).key.value)
        self.assertEqual('Foo', actual.get_item(0).value.value)
        self.assertEqual('Record(Slot("key", "Foo"))', str(actual))

    def test_map_request_get_key_item_complex(self):
        # Given
        mock_person = MockPerson('Bar', 29)
        map_request = MapRequest(mock_person, 1)
        # When
        actual = map_request.get_key_item()
        # Then
        self.assertIsInstance(actual, RecordMap)
        self.assertIsInstance(actual.get_item(0), Slot)
        self.assertEqual('key', actual.get_item(0).key.value)
        self.assertIsInstance(actual.get_item(0).value, RecordMap)
        self.assertIsInstance(actual.get_item(0).value.get_item(0), Attr)
        self.assertEqual('MockPerson', actual.get_item(0).value.get_item(0).key.value)
        self.assertIsInstance(actual.get_item(0).value.get_item(1), Slot)
        self.assertEqual('name', actual.get_item(0).value.get_item(1).key.value)
        self.assertEqual('Bar', actual.get_item(0).value.get_item(1).value.value)
        self.assertIsInstance(actual.get_item(0).value.get_item(2), Slot)
        self.assertEqual('age', actual.get_item(0).value.get_item(2).key.value)
        self.assertEqual(29, actual.get_item(0).value.get_item(2).value.value)
        self.assertEqual('Record(Slot("key", Record(Attr("MockPerson"), Slot("name", "Bar"), Slot("age", 29))))',
                         str(actual))

    def test_map_request_get_value_item_primitive(self):
        # Given
        map_request = MapRequest('Foo', 23)
        # When
        actual = map_request.get_value_item()
        # Then
        self.assertIsInstance(actual, Num)
        self.assertEqual(23, actual.value)
        self.assertEqual('23', str(actual))

    def test_map_request_get_value_item_complex(self):
        # Given
        mock_person = MockPerson('Foo', 20)
        map_request = MapRequest('Foo', mock_person)
        # When
        actual = map_request.get_value_item()
        # Then
        self.assertIsInstance(actual, RecordMap)
        self.assertIsInstance(actual.get_item(0), Attr)
        self.assertEqual('MockPerson', actual.get_item(0).key.value)
        self.assertIsInstance(actual.get_item(1), Slot)
        self.assertEqual('name', actual.get_item(1).key.value)
        self.assertEqual('Foo', actual.get_item(1).value.value)
        self.assertIsInstance(actual.get_item(2), Slot)
        self.assertEqual('age', actual.get_item(2).key.value)
        self.assertEqual(20, actual.get_item(2).value.value)
        self.assertEqual('Record(Attr("MockPerson"), Slot("name", "Foo"), Slot("age", 20))', str(actual))

    def test_update_request_to_record(self):
        # Given
        update_request = UpdateRequest('Moo', 21)
        # When
        actual = update_request.to_record()
        # Then
        self.assertIsInstance(actual, RecordMap)
        self.assertIsInstance(actual.get_item(0), Attr)
        self.assertEqual('update', actual.get_item(0).key.value)
        self.assertIsInstance(actual.get_item(0).value, RecordMap)
        self.assertIsInstance(actual.get_item(0).value.get_item(0), Slot)
        self.assertEqual('key', actual.get_item(0).value.get_item(0).key.value)
        self.assertEqual('Moo', actual.get_item(0).value.get_item(0).value.value)
        self.assertIsInstance(actual.get_item(1), Num)
        self.assertEqual(21, actual.get_item(1).value)
        self.assertEqual('Record(Attr("update", Record(Slot("key", "Moo"))), 21)', str(actual))

    def test_remove_request_to_record(self):
        # Given
        remove_request = RemoveRequest('Boo', 99)
        # When
        actual = remove_request.to_record()
        # Then
        self.assertIsInstance(actual, RecordMap)
        self.assertIsInstance(actual.get_item(0), Attr)
        self.assertEqual('remove', actual.get_item(0).key.value)
        self.assertIsInstance(actual.get_item(0).value, RecordMap)
        self.assertIsInstance(actual.get_item(0).value.get_item(0), Slot)
        self.assertEqual('key', actual.get_item(0).value.get_item(0).key.value)
        self.assertEqual('Boo', actual.get_item(0).value.get_item(0).value.value)
        self.assertEqual('Record(Attr("remove", Record(Slot("key", "Boo"))))', str(actual))

    @async_test
    async def test_convert_to_async_function(self):
        # Given
        function = mock_func
        # When
        actual = convert_to_async(function)
        response = await actual()
        # Then
        self.assertIsInstance(actual, Callable)
        self.assertTrue(inspect.iscoroutinefunction(actual))
        self.assertEqual('mock_func_response', response)
