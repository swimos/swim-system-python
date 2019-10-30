import unittest

from swim import Record, Num, Attr, Slot, Text, RecordMap, Bool, Item, Extant, Absent, Value, Field
from test.test_utils import CustomString


class TestStructs(unittest.TestCase):

    def test_item_concat_single_num(self):
        # Given
        headers = Record.create().slot('node', 'foo').slot('lane', 'bar')
        body = Num.create_from(42)
        # When
        actual = Attr.create_attr('tag', headers).concat(body)
        # Then
        self.assertEqual(2, actual.size)
        self.assertIsInstance(actual.get_items()[0], Attr)
        self.assertIsInstance(actual.get_items()[1], Num)
        self.assertEqual(42, actual.get_items()[1].value)

    def test_item_concat_single_record(self):
        # Given
        headers = Record.create().slot('node', 'foo').slot('lane', 'bar')
        body = Record.create().slot('attr', 'hello').slot('message', 'world')
        # When
        actual = Attr.create_attr('tag', headers).concat(body)
        # Then
        self.assertEqual(3, actual.size)
        self.assertIsInstance(actual.get_items()[0], Attr)
        self.assertIsInstance(actual.get_items()[1], Slot)
        self.assertIsInstance(actual.get_items()[2], Slot)
        self.assertEqual('attr', actual.get_items()[1].key.value)
        self.assertEqual('hello', actual.get_items()[1].value.value)
        self.assertEqual('message', actual.get_items()[2].key.value)
        self.assertEqual('world', actual.get_items()[2].value.value)

    def test_item_concat_multiple_text(self):
        # Given
        headers = Record.create().slot('node', 'foo').slot('lane', 'bar')
        headers.add(Num.create_from(42))
        body = Text.create_from('Polly the parrot')
        # When
        actual = headers.concat(body)
        # Then
        self.assertEqual(2, actual.size)
        self.assertIsInstance(actual.get_items()[0], RecordMap)
        self.assertEqual(3, actual.get_items()[0].size)
        self.assertIsInstance(actual.get_items()[1], Text)
        self.assertEqual('Polly the parrot', actual.get_items()[1].value)

    def test_item_concat_multiple_record(self):
        # Given
        headers = Record.create().slot('node', 'foo').slot('lane', 'bar')
        headers.add(Record.create().slot('node', 'boo').slot('lane', 'far'))
        body = Record.create().slot('node', 'poo').slot('lane', 'car')
        # When
        actual = headers.concat(body)
        # Then
        self.assertEqual(3, actual.size)
        self.assertIsInstance(actual.get_items()[0], RecordMap)
        self.assertEqual(3, actual.get_items()[0].size)
        self.assertIsInstance(actual.get_items()[1], Slot)
        self.assertEqual('node', actual.get_items()[1].key.value)
        self.assertEqual('poo', actual.get_items()[1].value.value)
        self.assertEqual('lane', actual.get_items()[2].key.value)
        self.assertEqual('car', actual.get_items()[2].value.value)

    def test_item_concat_zero_bool(self):
        # Given
        headers = Record.create()
        body = Bool.create_from(True)
        # When
        actual = headers.concat(body)
        # Then
        self.assertEqual(2, actual.size)
        self.assertIsInstance(actual.get_items()[0], RecordMap)
        self.assertEqual(0, actual.get_items()[0].size)
        self.assertIsInstance(actual.get_items()[1], Bool)
        self.assertEqual(True, actual.get_items()[1].value)

    def test_item_concat_zero_record(self):
        # Given
        headers = Record.create()
        body = Record.create().slot('node', 'moo').slot('lane', 'cow')
        # When
        actual = headers.concat(body)
        # Then
        self.assertEqual(3, actual.size)
        self.assertIsInstance(actual.get_items()[0], RecordMap)
        self.assertEqual(0, actual.get_items()[0].size)
        self.assertIsInstance(actual.get_items()[1], Slot)
        self.assertIsInstance(actual.get_items()[2], Slot)
        self.assertEqual('node', actual.get_items()[1].key.value)
        self.assertEqual('moo', actual.get_items()[1].value.value)
        self.assertEqual('lane', actual.get_items()[2].key.value)
        self.assertEqual('cow', actual.get_items()[2].value.value)

    def test_item_extant(self):
        # Given
        actual = Item.extant()
        # Then
        self.assertEqual(Extant.get_extant(), actual)

    def test_item_absent(self):
        # Given
        actual = Item.absent()
        # Then
        self.assertEqual(Absent.get_absent(), actual)

    def test_item_create_from_item(self):
        # Given
        record = Record.create().slot('node', 'boo').slot('lane', 'ghost')
        # When
        actual = Item.create_from(record)
        # Then
        self.assertIsInstance(actual, RecordMap)
        self.assertEqual(2, actual.size)
        self.assertEqual('node', actual.get_items()[0].key.value)
        self.assertEqual('boo', actual.get_items()[0].value.value)
        self.assertEqual('lane', actual.get_items()[1].key.value)
        self.assertEqual('ghost', actual.get_items()[1].value.value)

    def test_item_create_from_tuple(self):
        # Given
        record = {'node': 'boo'}
        # When
        dict()
        actual = Item.create_from(record)
        # Then
        self.assertIsInstance(actual, Slot)
        self.assertEqual('node', actual.key)
        self.assertEqual('boo', actual.value)

    def test_item_create_from_other(self):
        # Given
        record = 'monkey'
        # When
        actual = Item.create_from(record)
        # Then
        self.assertIsInstance(actual, Text)
        self.assertEqual('monkey', actual.value)

    def test_create_attr_from_text_key(self):
        # Given
        key = Text.create_from('Ghost')
        value = 'Boo'
        # When
        actual = Attr.create_attr(key, value)
        # Then
        self.assertIsInstance(actual.key, Text)
        self.assertEqual('Ghost', actual.key.value)
        self.assertEqual('Boo', actual.value)

    def test_create_attr_from_string_key(self):
        # Given
        key = 'Foo'
        value = Text.create_from('Bar')
        # When
        actual = Attr.create_attr(key, value)
        # Then
        self.assertIsInstance(actual.key, Text)
        self.assertEqual('Foo', actual.key.value)
        self.assertIsInstance(actual.value, Text)
        self.assertEqual('Bar', actual.value.value)

    def test_create_attr_from_invalid_key(self):
        # Given
        key = 34
        value = 'Bar'
        # When
        with self.assertRaises(TypeError) as error:
            Attr.create_attr(key, value)
        # Then
        message = error.exception.args[0]
        self.assertEqual('Invalid key: 34', message)

    def test_create_attr_from_empty_key(self):
        # Given
        key = None
        value = 'Bar'
        # When
        with self.assertRaises(TypeError) as error:
            Attr.create_attr(key, value)
        # Then
        message = error.exception.args[0]
        self.assertEqual('Empty key for attribute!', message)

    def test_create_attr_from_empty_value(self):
        # Given
        key = 'Foo'
        value = None
        # When
        with self.assertRaises(TypeError) as error:
            Attr.create_attr(key, value)
        # Then
        message = error.exception.args[0]
        self.assertEqual('Empty value for attribute!', message)

    def test_key_equals_str_true(self):
        # Given
        attribute = Attr.create_attr('Foo', 'Bar')
        # When
        actual = attribute.key_equals('Foo')
        # Then
        self.assertTrue(actual)

    def test_key_equals_str_false(self):
        # Given
        attribute = Attr.create_attr('Foo', 'Bar')
        # When
        actual = attribute.key_equals('Moo')
        # Then
        self.assertFalse(actual)

    def test_key_equals_attr_true(self):
        # Given
        attribute = Attr.create_attr('Hello', 'World')
        item = Attr.create_attr('Hello', 'Friend')
        # When
        actual = attribute.key_equals(item)
        # Then
        self.assertTrue(actual)

    def test_key_equals_attr_false(self):
        # Given
        attribute = Attr.create_attr('Hello', 'World')
        item = Attr.create_attr('Goodbye', 'Friend')
        # When
        actual = attribute.key_equals(item)
        # Then
        self.assertFalse(actual)

    def test_key_equals_other_false(self):
        # Given
        attribute = Attr.create_attr('Hello', 'World')
        item = CustomString('Hello')
        # When
        actual = attribute.key_equals(item)
        # Then
        self.assertTrue(actual)

    def test_key_equals_other_true(self):
        # Given
        attribute = Attr.create_attr('Hello', 'World')
        item = CustomString('Goodbye')
        # When
        actual = attribute.key_equals(item)
        # Then
        self.assertFalse(actual)

    def test_empty_value(self):
        # Given
        actual = Value()
        # Then
        self.assertEqual(Absent.get_absent(), actual.key)
        self.assertEqual(Absent.get_absent(), actual.value)
        self.assertEqual(0, actual.length)

    def test_create_value_from_object_none(self):
        # Given
        obj = None
        # When
        actual = Value.create_from(obj)
        # Then
        self.assertEqual(Extant.get_extant(), actual)

    def test_create_value_from_object_value(self):
        # Given
        obj = Text.create_from('Boom')
        # When
        actual = Value.create_from(obj)
        # Then
        self.assertIsInstance(actual, Value)
        self.assertEqual('Boom', actual.value)

    def test_create_value_from_object_str(self):
        # Given
        obj = 'Dog'
        # When
        actual = Value.create_from(obj)
        # Then
        self.assertIsInstance(actual, Text)
        self.assertEqual('Dog', actual.value)

    def test_create_value_from_object_int(self):
        # Given
        obj = 33
        # When
        actual = Value.create_from(obj)
        # Then
        self.assertIsInstance(actual, Num)
        self.assertEqual(33, actual.value)

    def test_create_value_from_object_float(self):
        # Given
        obj = 3.14
        # When
        actual = Value.create_from(obj)
        # Then
        self.assertIsInstance(actual, Num)
        self.assertEqual(3.14, actual.value)

    def test_create_value_from_object_boolean(self):
        # Given
        obj = True
        # When
        actual = Value.create_from(obj)
        # Then
        self.assertIsInstance(actual, Num)
        self.assertEqual(True, actual.value)

    def test_create_value_from_object_invalid(self):
        # Given
        obj = CustomString('Foo')
        # When
        with self.assertRaises(TypeError) as error:
            Value.create_from(obj)
        # Then
        message = error.exception.args[0]
        self.assertEqual('CustomString(Foo) cannot be converted to Value!', message)

    def test_create_text_from_string(self):
        # Given
        string = 'Tea'
        # When
        actual = Text.create_from(string)
        # Then
        self.assertIsInstance(actual, Text)
        self.assertEqual('Tea', actual.value)

    def test_create_text_from_empty_string(self):
        # Given
        string = ''
        # When
        actual = Text.create_from(string)
        # Then
        self.assertIsInstance(actual, Text)
        self.assertEqual('', actual.value)

    def test_text_get_empty_first_time(self):
        # When
        actual = Text.get_empty()
        # Then
        self.assertEqual('', actual.value)
        self.assertEqual(Text.empty, actual)

    def test_text_get_empty_multiple_times(self):
        # Given
        Text.get_empty()
        # When
        actual = Text.get_empty()
        # Then
        self.assertEqual('', actual.value)
        self.assertEqual(Text.empty, actual)

    def test_text_string_value(self):
        # Given
        text = Text.create_from('Dog')
        # When
        actual = text.get_string_value()
        # Then
        self.assertIsInstance(actual, str)
        self.assertEqual('Dog', actual)
