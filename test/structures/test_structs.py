import unittest

from swimai import Record, Num, Attr, Slot, Text, RecordMap, Bool, Item, Extant, Absent, Value, RecordFlags, RecordMapView, ValueBuilder
from test.test_utils import CustomString, CustomItem


class TestStructs(unittest.TestCase):

    def test_item_concat_single_num(self):
        # Given
        headers = Record.create().add_slot('node', 'foo').add_slot('lane', 'bar')
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
        headers = Record.create().add_slot('node', 'foo').add_slot('lane', 'bar')
        body = Record.create().add_slot('attr', 'hello').add_slot('message', 'world')
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
        headers = Record.create().add_slot('node', 'foo').add_slot('lane', 'bar')
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
        headers = Record.create().add_slot('node', 'foo').add_slot('lane', 'bar')
        headers.add(Record.create().add_slot('node', 'boo').add_slot('lane', 'far'))
        body = Record.create().add_slot('node', 'poo').add_slot('lane', 'car')
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
        self.assertTrue(actual.get_items()[1].value)

    def test_item_concat_zero_record(self):
        # Given
        headers = Record.create()
        body = Record.create().add_slot('node', 'moo').add_slot('lane', 'cow')
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
        record = Record.create().add_slot('node', 'boo').add_slot('lane', 'ghost')
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
        self.assertEqual(0, actual.size)

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
        self.assertIsInstance(actual, Bool)
        self.assertTrue(actual.value)

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

    def test_num_integer(self):
        # When
        num = Num(33)
        # Then
        self.assertEqual(33, num.value)
        self.assertEqual(33, num.get_num_value())

    def test_num_float(self):
        # When
        num = Num(0.11)
        # Then
        self.assertEqual(0.11, num.value)
        self.assertEqual(0.11, num.get_num_value())

    def test_create_num_from_positive_integer(self):
        # Given
        num = 99
        # When
        actual = Num.create_from(num)
        # Then
        self.assertIsInstance(actual, Num)
        self.assertEqual(99, actual.get_num_value())

    def test_create_num_from_negative_integer(self):
        # Given
        num = -99
        # When
        actual = Num.create_from(num)
        # Then
        self.assertIsInstance(actual, Num)
        self.assertEqual(-99, actual.get_num_value())

    def test_create_num_from_positive_float(self):
        # Given
        num = 9.9
        # When
        actual = Num.create_from(num)
        # Then
        self.assertIsInstance(actual, Num)
        self.assertEqual(9.9, actual.get_num_value())

    def test_create_num_from_negative_float(self):
        # Given
        num = -9.9
        # When
        actual = Num.create_from(num)
        # Then
        self.assertIsInstance(actual, Num)
        self.assertEqual(-9.9, actual.get_num_value())

    def test_bool_false(self):
        # Given
        boolean = Bool(True)
        # Then
        self.assertTrue(boolean.value)
        self.assertTrue(boolean.get_bool_value())

    def test_bool_true(self):
        # Given
        boolean = Bool(False)
        # Then
        self.assertFalse(boolean.value)
        self.assertFalse(boolean.get_bool_value())

    def test_create_bool_from_true_once(self):
        # Given
        boolean = True
        # When
        actual = Bool.create_from(boolean)
        # Then
        self.assertIsInstance(actual, Bool)
        self.assertEqual(Bool.TRUE, actual)
        self.assertTrue(actual.get_bool_value())

    def test_create_bool_from_true_twice(self):
        # Given
        boolean = True
        Bool.create_from(boolean)
        # When
        actual = Bool.create_from(boolean)
        # Then
        self.assertIsInstance(actual, Bool)
        self.assertEqual(Bool.TRUE, actual)
        self.assertTrue(actual.get_bool_value())

    def test_create_bool_from_false_once(self):
        # Given
        boolean = False
        # When
        actual = Bool.create_from(boolean)
        # Then
        self.assertIsInstance(actual, Bool)
        self.assertEqual(Bool.FALSE, actual)
        self.assertFalse(actual.get_bool_value())

    def test_create_bool_from_false_twice(self):
        # Given
        boolean = False
        Bool.create_from(boolean)
        # When
        actual = Bool.create_from(boolean)
        # Then
        self.assertIsInstance(actual, Bool)
        self.assertEqual(Bool.FALSE, actual)
        self.assertFalse(actual.get_bool_value())

    def test_get_absent_once(self):
        # When
        actual = Absent.get_absent()
        # Then
        self.assertIsInstance(actual, Absent)
        self.assertEqual(Absent.absent, actual)
        self.assertEqual(Absent.get_absent(), actual)

    def test_get_absent_twice(self):
        # Given
        Absent.get_absent()
        # When
        actual = Absent.get_absent()
        # Then
        self.assertIsInstance(actual, Absent)
        self.assertEqual(Absent.absent, actual)
        self.assertEqual(Absent.get_absent(), actual)

    def test_get_extant_once(self):
        # When
        actual = Extant.get_extant()
        # Then
        self.assertIsInstance(actual, Extant)
        self.assertEqual(Extant.extant, actual)
        self.assertEqual(Extant.get_extant(), actual)

    def test_get_extant_twice(self):
        # Given
        Extant.get_extant()
        # When
        actual = Extant.get_extant()
        # Then
        self.assertIsInstance(actual, Extant)
        self.assertEqual(Extant.extant, actual)
        self.assertEqual(Extant.get_extant(), actual)

    def test_slot_key_value(self):
        # Given
        slot = Slot('Foo', 'Bar')
        # Then
        self.assertIsInstance(slot, Slot)
        self.assertEqual('Foo', slot.key)
        self.assertEqual('Bar', slot.value)

    def test_slot_key_only(self):
        # Given
        slot = Slot('Foo')
        # Then
        self.assertIsInstance(slot, Slot)
        self.assertEqual('Foo', slot.key)
        self.assertEqual(Extant.get_extant(), slot.value)

    def test_create_slot_key_value(self):
        # Given
        key = 'dog'
        value = 'bark'
        # When
        actual = Slot.create_slot(key, value)
        # Then
        self.assertIsInstance(actual, Slot)
        self.assertEqual('dog', actual.key)
        self.assertEqual('bark', actual.value)

    def test_create_slot_key_only(self):
        # Given
        key = 'dog'
        # When
        actual = Slot.create_slot(key)
        # Then
        self.assertIsInstance(actual, Slot)
        self.assertEqual('dog', actual.key)
        self.assertEqual(Extant.get_extant(), actual.value)

    def test_create_slot_no_key(self):
        # Given
        key = None
        # When
        with self.assertRaises(TypeError) as error:
            Slot.create_slot(key)
        # Then
        message = error.exception.args[0]
        self.assertEqual('Empty key for slot!', message)

    def test_record_create(self):
        # When
        actual = Record.create()
        # Then
        self.assertIsInstance(actual, RecordMap)

    def test_record_add_all_single(self):
        # Given
        actual = Record.create()
        item = Text.create_from('Foo')
        items = [item]
        # When
        actual_response = actual.add_all(items)
        # Then
        self.assertEqual(1, actual.size)
        self.assertEqual(1, actual.item_count)
        self.assertEqual(item, actual.get_item(0))
        self.assertTrue(actual_response)

    def test_record_add_all_multiple(self):
        # Given
        actual = Record.create()
        first_item = Text.create_from('Foo')
        second_item = Text.create_from('Bar')
        third_item = Text.create_from('Baz')
        items = [first_item, second_item, third_item]
        # When
        actual_response = actual.add_all(items)
        # Then
        self.assertEqual(3, actual.size)
        self.assertEqual(3, actual.item_count)
        self.assertEqual(first_item, actual.get_item(0))
        self.assertEqual(second_item, actual.get_item(1))
        self.assertEqual(third_item, actual.get_item(2))
        self.assertTrue(actual_response)

    def test_record_add_all_empty(self):
        # Given
        actual = Record.create()
        items = []
        # When
        actual_response = actual.add_all(items)
        # Then
        self.assertEqual(0, actual.size)
        self.assertEqual(0, actual.item_count)
        self.assertEqual(False, actual_response)

    def test_record_add_slot_key_item_value_item(self):
        # Given
        actual = Record.create()
        key = Text.create_from('Good')
        value = Text.create_from('Dog')
        # When
        actual = actual.add_slot(key, value)
        # Then
        self.assertEqual(1, actual.size)
        self.assertIsInstance(actual, Record)
        self.assertIsInstance(actual.get_item(0), Slot)
        self.assertEqual(key, actual.get_item(0).key)
        self.assertEqual(value, actual.get_item(0).value)

    def test_record_add_slot_key_string_value_item(self):
        # Given
        actual = Record.create()
        key = 'Baz'
        value = Text.create_from('Qux')
        # When
        actual = actual.add_slot(key, value)
        # Then
        self.assertEqual(1, actual.size)
        self.assertIsInstance(actual, Record)
        self.assertIsInstance(actual.get_item(0), Slot)
        self.assertEqual('Baz', actual.get_item(0).key.value)
        self.assertEqual('Qux', actual.get_item(0).value.value)

    def test_record_add_slot_key_item_value_string(self):
        # Given
        actual = Record.create()
        key = Text.create_from('Foo')
        value = 'Bar'
        # When
        actual = actual.add_slot(key, value)
        # Then
        self.assertEqual(1, actual.size)
        self.assertIsInstance(actual, Record)
        self.assertIsInstance(actual.get_item(0), Slot)
        self.assertEqual('Foo', actual.get_item(0).key.value)
        self.assertEqual('Bar', actual.get_item(0).value.value)

    def test_record_add_slot_key_string_value_string(self):
        # Given
        actual = Record.create()
        key = 'Wibble'
        value = 'Wobble'
        # When
        actual = actual.add_slot(key, value)
        # Then
        self.assertEqual(1, actual.size)
        self.assertIsInstance(actual, Record)
        self.assertIsInstance(actual.get_item(0), Slot)
        self.assertEqual('Wibble', actual.get_item(0).key.value)
        self.assertEqual('Wobble', actual.get_item(0).value.value)

    def test_record_get_headers_record(self):
        # Given
        record = Record.create()
        body = Record.create()
        body.add_slot('Foo', 'Bar')
        record.add(Attr.create_attr(Text.create_from('cat'), body))
        # When
        actual = record.get_headers('cat')
        # Then
        self.assertIsInstance(actual, Record)
        self.assertEqual(1, actual.size)
        self.assertEqual('Foo', actual.get_item(0).key.value)
        self.assertEqual('Bar', actual.get_item(0).value.value)

    def test_record_get_headers_object(self):
        # Given
        record = Record.create()
        body = Slot.create_slot('Baz', 'Qux')
        record.add(Attr.create_attr(Text.create_from('dog'), body))
        # When
        actual = record.get_headers('dog')
        # Then
        self.assertIsInstance(actual, Record)
        self.assertEqual(1, actual.size)
        self.assertEqual('Baz', actual.get_item(0).key)
        self.assertEqual('Qux', actual.get_item(0).value)

    def test_record_get_headers_none(self):
        # Given
        record = Record.create()
        body = Slot.create_slot('Hello', 'World')
        record.add(Attr.create_attr(Text.create_from('mouse'), body))
        # When
        actual = record.get_headers('bird')
        # Then
        self.assertIsNone(actual)

    def test_record_get_head(self):
        # Given
        record = Record.create()
        body = Slot.create_slot('Hello', 'World')
        first_item = Attr.create_attr(Text.create_from('bird'), body)
        second_item = Attr.create_attr(Text.create_from('frog'), body)
        record.add(first_item)
        record.add(second_item)
        # When
        actual = record.get_head()
        # Then
        self.assertEqual(first_item, actual)
        self.assertNotEqual(second_item, actual)

    def test_record_bind(self):
        # Given
        record = Record.create()
        body = Slot.create_slot('Hello', 'Friend')
        first_item = Attr.create_attr(Text.create_from('dog'), body)
        record.add(first_item)
        # When
        actual = record.bind()
        # Then
        self.assertEqual(record, actual)

    def test_record_map_size_empty(self):
        # Given
        record = RecordMap.create()
        # When
        actual = record.size
        # Then
        self.assertEqual(0, actual)

    def test_record_map_size_one(self):
        # Given
        record = RecordMap.create_record_map(Text.create_from('Test'))
        # When
        actual = record.size
        # Then
        self.assertEqual(1, actual)

    def test_record_map_size_three(self):
        # Given
        record = RecordMap.create()
        record.add(Text.create_from('This'))
        record.add(Text.create_from('is'))
        record.add(Text.create_from('test'))
        # When
        actual = record.size
        # Then
        self.assertEqual(3, actual)

    def test_record_map_tag_attr(self):
        # Given
        record = RecordMap.create()
        record.add(Attr.create_attr('Foo', 'Bar'))
        # When
        actual = record.tag
        # Then
        self.assertEqual('Foo', actual)

    def test_record_map_tag_slot(self):
        # Given
        record = RecordMap.create()
        record.add(Slot.create_slot('Foo', 'Bar'))
        # When
        actual = record.tag
        # Then
        self.assertEqual(None, actual)

    def test_record_map_tag_empty(self):
        # Given
        record = RecordMap.create()
        # When
        actual = record.tag
        # Then
        self.assertEqual(None, actual)

    def test_record_map_create(self):
        # When
        actual = RecordMap.create()
        # Then
        self.assertEqual(0, actual.size)
        self.assertEqual(RecordFlags.ALIASED.value, actual.flags)

    def test_record_map_create_with_empty(self):
        # Given
        item = None
        # When
        actual = RecordMap.create_record_map(item)
        # Then
        self.assertEqual(1, actual.size)
        self.assertEqual(0, actual.field_count)
        self.assertEqual(Extant.get_extant(), actual.get_item(0))

    def test_record_map_create_with_field(self):
        # Given
        item = Attr.create_attr('Foo', 'Bar')
        # When
        actual = RecordMap.create_record_map(item)
        # Then
        self.assertEqual(1, actual.size)
        self.assertEqual(1, actual.field_count)
        self.assertEqual(item, actual.get_item(0))

    def test_record_map_create_with_value(self):
        # Given
        item = Value.create_from('Baz')
        # When
        actual = RecordMap.create_record_map(item)
        # Then
        self.assertEqual(1, actual.size)
        self.assertEqual(0, actual.field_count)
        self.assertEqual(item, actual.get_item(0))

    def test_record_map_get_item_existing(self):
        # Given
        record_map = RecordMap.create()
        first_item = Attr.create_attr('First', '1st')
        second_item = Attr.create_attr('Second', '2nd')
        third_item = Attr.create_attr('Thrid', '3rd')
        record_map.add(first_item)
        record_map.add(second_item)
        record_map.add(third_item)
        # When
        actual = record_map.get_item(1)
        # Then
        self.assertEqual(second_item, actual)

    def test_record_map_get_item_underflow(self):
        # Given
        record_map = RecordMap.create()
        first_item = Attr.create_attr('First', '1st')
        second_item = Attr.create_attr('Second', '2nd')
        record_map.add(first_item)
        record_map.add(second_item)
        # When
        actual = record_map.get_item(-1)
        # Then
        self.assertEqual(Absent.get_absent(), actual)

    def test_record_map_get_item_overflow(self):
        # Given
        record_map = RecordMap.create()
        first_item = Attr.create_attr('First', '1st')
        record_map.add(first_item)
        # When
        actual = record_map.get_item(2)
        # Then
        self.assertEqual(Absent.get_absent(), actual)

    def test_record_map_get_items_empty(self):
        # Given
        record_map = RecordMap.create()
        # When
        actual = record_map.get_items()
        # Then
        self.assertEqual([], actual)

    def test_record_map_get_items_single(self):
        # Given
        record_map = RecordMap.create()
        first_item = Attr.create_attr('Hello', 'World')
        record_map.add(first_item)
        # When
        actual = record_map.get_items()
        # Then
        self.assertEqual([first_item], actual)

    def test_record_map_get_items_multiple(self):
        # Given
        record_map = RecordMap.create()
        first_item = Attr.create_attr('Hello', 'World')
        second_item = Attr.create_attr('Bye', 'World')
        record_map.add(first_item)
        record_map.add(second_item)
        # When
        actual = record_map.get_items()
        # Then
        self.assertEqual([first_item, second_item], actual)

    def test_record_map_get_body_empty_without_head(self):
        # Given
        record_map = RecordMap.create()
        # When
        actual = record_map.get_body()
        # Then
        self.assertEqual(Absent.get_absent(), actual)

    def test_record_map_get_body_empty_with_head(self):
        # Given
        record_map = RecordMap.create()
        record_map.add(Attr.create_attr('Hello', 'World'))
        # When
        actual = record_map.get_body()
        # Then
        self.assertEqual(Absent.get_absent(), actual)

    def test_record_map_get_body_single_value(self):
        # Given
        record_map = RecordMap.create()
        body = Text.create_from('Moo')
        record_map.add(Attr.create_attr('Hello', 'World'))
        record_map.add(body)
        # When
        actual = record_map.get_body()
        # Then
        self.assertEqual(body, actual)

    def test_record_map_get_body_single_object(self):
        # Given
        record_map = RecordMap.create()
        body = Attr.create_attr('Moo', 'Moo')
        record_map.add(Attr.create_attr('Hello', 'World'))
        record_map.add(body)
        # When
        actual = record_map.get_body()
        # Then
        self.assertIsInstance(actual, RecordMap)
        self.assertEqual(body, actual.get_item(0))

    def test_record_map_get_body_multiple_(self):
        # Given
        record_map = RecordMap.create()
        first = Attr.create_attr('Moo', 'Moo')
        second = Attr.create_attr('Boo', 'Boo')
        record_map.add(Attr.create_attr('Goodbye', 'World'))
        record_map.add(first)
        record_map.add(second)
        # When
        actual = record_map.get_body()
        # Then
        self.assertIsInstance(actual, RecordMap)
        self.assertEqual(first, actual.get_item(0))
        self.assertEqual(second, actual.get_item(1))

    def test_record_immutable_map_add(self):
        # Given
        record_map = RecordMap.create()
        record_map.flags = RecordFlags.IMMUTABLE.value
        item = Attr.create_attr('Moo', 'Moo')
        # When
        with self.assertRaises(TypeError) as error:
            record_map.add(item)
        # Then
        message = error.exception.args[0]
        self.assertEqual('Cannot add item to immutable record!', message)

    def test_record_aliased_map_add(self):
        # Given
        record_map = RecordMap.create()
        record_map.flags = RecordFlags.ALIASED.value
        item = Attr.create_attr('Moo', 'Moo')
        # When
        actual_response = record_map.add(item)
        # Then
        self.assertTrue(actual_response)
        self.assertEqual([item], record_map.items)
        self.assertEqual(1, record_map.item_count)
        self.assertEqual(1, record_map.field_count)
        self.assertEqual(0, record_map.flags)
        self.assertEqual(None, record_map.fields)

    def test_record_mutable_map_add(self):
        # Given
        record_map = RecordMap.create()
        record_map.flags = 0
        item = Attr.create_attr('Foo', 'Foo')
        # When
        actual_response = record_map.add(item)
        # Then
        self.assertEqual([item], record_map.items)
        self.assertTrue(actual_response)
        self.assertEqual(1, record_map.item_count)
        self.assertEqual(1, record_map.field_count)

    def test_record_map_add_mutable_non_field(self):
        # Given
        record_map = RecordMap.create()
        record_map.flags = 0
        item = Value.create_from('Foo')
        # When
        actual_response = record_map.add(item)
        # Then
        self.assertEqual([item], record_map.items)
        self.assertTrue(actual_response)
        self.assertEqual(1, record_map.item_count)
        self.assertEqual(0, record_map.field_count)

    def test_record_map_add_mutable_field_with_hashtable_unique(self):
        # Given
        record_map = RecordMap.create()
        record_map.flags = 0
        first_item = Attr.create_attr('Foo', 'Foo')
        second_item = Attr.create_attr('Moo', 'Moo')

        # When
        record_map.add(first_item)
        record_map.contains_key('Foo')
        record_map.add(second_item)
        # Then
        self.assertEqual([first_item, second_item], record_map.items)
        self.assertEqual(2, record_map.item_count)
        self.assertEqual(2, record_map.field_count)
        self.assertEqual({'Foo': first_item, 'Moo': second_item}, record_map.fields)

    def test_record_map_add_mutable_field_with_hashtable_duplicate(self):
        # Given
        record_map = RecordMap.create()
        record_map.flags = 0
        first_item = Attr.create_attr('Boo', 'Foo')
        second_item = Attr.create_attr('Boo', 'Moo')
        # When
        record_map.add(first_item)
        record_map.add(second_item)
        record_map.contains_key('Boo')
        # Then
        self.assertEqual([first_item, second_item], record_map.items)
        self.assertEqual(2, record_map.item_count)
        self.assertEqual(2, record_map.field_count)
        self.assertEqual({'Boo': second_item}, record_map.fields)

    def test_record_map_add_aliased_non_field(self):
        # Given
        record_map = RecordMap.create()
        record_map.flags = 2
        item = Value.create_from('Boo')
        # When
        actual_response = record_map.add(item)
        # Then
        self.assertEqual([item], record_map.items)
        self.assertEqual(True, actual_response)
        self.assertEqual(1, record_map.item_count)
        self.assertEqual(0, record_map.field_count)

    def test_record_map_commit_mutable(self):
        # Given
        record_map = RecordMap.create()
        record_map.flags = 0
        # When
        actual = record_map.commit()
        # Then
        self.assertEqual(record_map, actual)
        self.assertEqual(RecordFlags.IMMUTABLE.value, actual.flags)

    def test_record_map_commit_aliased(self):
        # Given
        record_map = RecordMap.create()
        record_map.flags = 2
        # When
        actual = record_map.commit()
        # Then
        self.assertEqual(record_map, actual)
        self.assertEqual(3, actual.flags)

    def test_record_map_commit_immutable(self):
        # Given
        record_map = RecordMap.create()
        record_map.flags = 1
        # When
        actual = record_map.commit()
        # Then
        self.assertEqual(record_map, actual)
        self.assertEqual(1, actual.flags)

    def test_record_map_contains_key_value(self):
        # Given
        record_map = RecordMap.create()
        record_map.add(Attr.create_attr('Foo', 'Poo'))
        record_map.add(Attr.create_attr('Moo', 'Boo'))
        # When
        actual = record_map.contains_key(Text.create_from('Moo'))
        # Then
        self.assertTrue(actual)

    def test_record_map_contains_key_string(self):
        # Given
        record_map = RecordMap.create()
        record_map.add(Attr.create_attr('Foo', 'Poo'))
        record_map.add(Attr.create_attr('Moo', 'Boo'))
        # When
        actual = record_map.contains_key('Foo')
        # Then
        self.assertTrue(actual)

    def test_record_map_contains_key_duplicate(self):
        # Given
        record_map = RecordMap.create()
        record_map.add(Attr.create_attr('Foo', 'Poo'))
        record_map.add(Attr.create_attr('Foo', 'Boo'))
        # When
        actual = record_map.contains_key('Foo')
        # Then
        self.assertTrue(actual)

    def test_record_map_contains_key_false(self):
        # Given
        record_map = RecordMap.create()
        record_map.add(Attr.create_attr('Foo', 'Poo'))
        record_map.add(Attr.create_attr('Moo', 'Boo'))
        # When
        actual = record_map.contains_key('Poo')
        # Then
        self.assertFalse(actual)

    def test_record_map_contains_key_field_count_empty(self):
        # Given
        record_map = RecordMap.create()
        # When
        actual = record_map.contains_key('Poo')
        # Then
        self.assertFalse(actual)

    def test_record_map_branch_empty(self):
        # Given
        original_record = Record.create()
        original_record.flags = 0
        # When
        copy_record = original_record.branch()
        # Then
        self.assertEqual(original_record.items, copy_record.items)
        self.assertEqual(original_record.fields, copy_record.fields)
        self.assertEqual(original_record.item_count, copy_record.item_count)
        self.assertEqual(original_record.field_count, copy_record.field_count)
        self.assertEqual(2, original_record.flags)
        self.assertEqual(original_record.flags, copy_record.flags)

    def test_record_map_branch_single(self):
        # Given
        original_record = Record.create()
        original_record.flags = 0
        original_record.add(Attr.create_attr('Foo', 'Bar'))
        # When
        copy_record = original_record.branch()
        # Then
        self.assertEqual(2, original_record.flags)
        self.assertEqual(original_record.items, copy_record.items)
        self.assertEqual(original_record.fields, copy_record.fields)
        self.assertEqual(1, copy_record.item_count)
        self.assertEqual(1, copy_record.field_count)

    def test_record_map_branch_multiple(self):
        # Given
        original_record = Record.create()
        original_record.flags = 0
        original_record.add(Attr.create_attr('Foo', 'Bar'))
        original_record.add(Attr.create_attr('Baz', 'Qux'))
        # When
        copy_record = original_record.branch()
        # Then
        self.assertEqual(2, original_record.flags)
        self.assertEqual(original_record.items, copy_record.items)
        self.assertEqual(original_record.fields, copy_record.fields)
        self.assertEqual(2, copy_record.item_count)
        self.assertEqual(2, copy_record.field_count)

    def test_record_map_branch_with_hashtable(self):
        # Given
        original_record = Record.create()
        original_record.flags = 0
        original_record.add(Attr.create_attr('Bar', 'Baz'))
        original_record.contains_key('Bar')
        # When
        copy_record = original_record.branch()
        # Then
        self.assertIsNotNone(copy_record.fields)
        self.assertEqual(original_record.items, copy_record.items)
        self.assertEqual(original_record.fields, copy_record.fields)
        self.assertEqual(1, copy_record.item_count)
        self.assertEqual(1, copy_record.field_count)

    def test_record_map_branch_mutate_original(self):
        # Given
        original_record = Record.create()
        original_record.add(Attr.create_attr('K', 'V'))
        original_record.add(Attr.create_attr('A', 'B'))
        # When
        original_record.contains_key('K')
        copy_record = original_record.branch()
        original_record.add(Attr.create_attr(Text.create_from('P'), Text.create_from('V')))
        original_record.contains_key('K')
        # Then
        self.assertEqual(0, original_record.flags)
        self.assertEqual(2, copy_record.flags)
        self.assertNotEqual(original_record.items, copy_record.items)
        self.assertEqual(3, original_record.item_count)
        self.assertEqual(2, copy_record.item_count)
        self.assertEqual(3, original_record.field_count)
        self.assertEqual(2, copy_record.field_count)
        self.assertIsNotNone(original_record.fields)
        self.assertIsNotNone(copy_record.fields)
        self.assertEqual(3, len(original_record.fields))
        self.assertEqual(2, len(copy_record.fields))

    def test_record_map_branch_mutate_copy(self):
        # Given
        original_record = Record.create()
        original_record.add(Attr.create_attr('F', 'L'))
        original_record.add(Attr.create_attr('M', 'S'))
        # When
        original_record.contains_key('P')
        copy_record = original_record.branch()
        copy_record.add(Attr.create_attr(Text.create_from('P'), Text.create_from('V')))
        copy_record.add(Attr.create_attr(Text.create_from('T'), Text.create_from('B')))
        copy_record.contains_key('H')
        # Then
        self.assertEqual(2, original_record.flags)
        self.assertEqual(0, copy_record.flags)
        self.assertNotEqual(original_record.items, copy_record.items)
        self.assertEqual(2, original_record.item_count)
        self.assertEqual(4, copy_record.item_count)
        self.assertEqual(2, original_record.field_count)
        self.assertEqual(4, copy_record.field_count)
        self.assertIsNotNone(original_record.fields)
        self.assertIsNotNone(copy_record.fields)
        self.assertEqual(2, len(original_record.fields))
        self.assertEqual(4, len(copy_record.fields))

    def test_record_map_view(self):
        # Given
        record = Record.create()
        record.add(Attr.create_attr('A', 'B'))
        record.add(Attr.create_attr('C', 'D'))
        record.add(Attr.create_attr('E', 'F'))
        record.add(Attr.create_attr('G', 'H'))
        # When
        actual = RecordMapView(record, 1, 3)
        # Then
        self.assertEqual(2, actual.size)
        self.assertEqual(1, actual.lower)
        self.assertEqual(3, actual.upper)

    def test_record_map_view_get_item_existing(self):
        # Given
        record = Record.create()
        record.add(Attr.create_attr('Z', 'X'))
        record.add(Attr.create_attr('Y', 'W'))
        record.add(Attr.create_attr('P', 'L'))
        record.add(Attr.create_attr('M', 'N'))
        # When
        actual = RecordMapView(record, 1, 3)
        # Then
        self.assertEqual('W', actual.get_item(0).value)
        self.assertEqual('L', actual.get_item(1).value)

    def test_record_map_view_get_item_underflow(self):
        # Given
        record = Record.create()
        record.add(Attr.create_attr('G', 'V'))
        record.add(Attr.create_attr('H', 'B'))
        record.add(Attr.create_attr('J', 'N'))
        record.add(Attr.create_attr('K', 'M'))
        # When
        actual = RecordMapView(record, 1, 3)
        # Then
        self.assertEqual(Absent.get_absent(), actual.get_item(-1).value)

    def test_record_map_view_get_item_overflow(self):
        # Given
        record = Record.create()
        record.add(Attr.create_attr('F', 'V'))
        record.add(Attr.create_attr('Y', 'B'))
        record.add(Attr.create_attr('U', 'N'))
        record.add(Attr.create_attr('I', 'M'))
        # When
        actual = RecordMapView(record, 1, 3)
        # Then
        self.assertEqual(Absent.get_absent(), actual.get_item(3).value)

    def test_record_map_view_get_items_none(self):
        # Given
        record = Record.create()
        record.add(Attr.create_attr('U', 'N'))
        record.add(Attr.create_attr('I', 'M'))
        # When
        actual = RecordMapView(record, 4, 5)
        # Then
        self.assertEqual([], actual.get_items())

    def test_record_map_view_get_items_single(self):
        # Given
        record = Record.create()
        first = Attr.create_attr('U', 'N')
        second = Attr.create_attr('A', 'N')
        third = Attr.create_attr('I', 'M')
        record.add(first)
        record.add(second)
        record.add(third)
        # When
        actual = RecordMapView(record, 1, 2)
        # Then
        self.assertEqual([second], actual.get_items())

    def test_record_map_view_get_items_multiple(self):
        # Given
        record = Record.create()
        first = Attr.create_attr('A', 'K')
        second = Attr.create_attr('K', 'P')
        third = Attr.create_attr('Q', 'F')
        record.add(first)
        record.add(second)
        record.add(third)
        # When
        actual = RecordMapView(record, 1, 3)
        # Then
        self.assertEqual([second, third], actual.get_items())

    def test_record_map_view_immutable_add(self):
        # Given
        record = Record.create()
        record.add(Attr.create_attr('L', 'K'))
        record.add(Attr.create_attr('T', 'P'))
        record.add(Attr.create_attr('R', 'F'))
        new_item = Attr.create_attr('New', 'Item')
        record.flags = 1
        record_map_view = RecordMapView(record, 1, 3)
        # When
        with self.assertRaises(TypeError) as error:
            record_map_view.add(new_item, 2)
        # Then
        message = error.exception.args[0]
        self.assertEqual('Cannot add item to immutable record!', message)

    def test_record_map_view_out_of_bounds_add(self):
        # Given
        record = Record.create()
        record.add(Attr.create_attr('T', 'K'))
        record.add(Attr.create_attr('I', 'P'))
        record.add(Attr.create_attr('M', 'F'))
        new_item = Attr.create_attr('Foo', 'Bar')
        record_map_view = RecordMapView(record, 1, 3)
        # When
        with self.assertRaises(IndexError) as error:
            record_map_view.add(new_item, 5)
        # Then
        message = error.exception.args[0]
        self.assertEqual(f'Index 5 is out of range!', message)

    def test_record_map_view_add_field(self):
        # Given
        record = Record.create()
        record.add(Attr.create_attr('T', 'K'))
        record.add(Attr.create_attr('C', 'P'))
        record.add(Attr.create_attr('M', 'F'))
        new_item = Attr.create_attr('Field', 'Item')
        record_map_view = RecordMapView(record, 1, 3)
        # When
        actual_response = record_map_view.add(new_item, 2)
        # Then
        self.assertTrue(actual_response)
        self.assertEqual(3, record_map_view.size)
        self.assertEqual(4, record_map_view.upper)
        self.assertEqual(1, record_map_view.lower)
        self.assertEqual(new_item, record_map_view.get_item(2))
        self.assertEqual(4, record_map_view.record.item_count)
        self.assertEqual(4, record_map_view.record.field_count)
        self.assertEqual(0, record_map_view.record.flags)
        self.assertEqual(None, record_map_view.record.fields)

    def test_record_map_view_add_value(self):
        # Given
        record = Record.create()
        record.add(Attr.create_attr('T', 'K'))
        record.add(Attr.create_attr('T', 'P'))
        new_item = Text.create_from('Text')
        record_map_view = RecordMapView(record, 0, 2)
        # When
        actual_response = record_map_view.add(new_item, 1)
        # Then
        self.assertTrue(actual_response)
        self.assertEqual(3, record_map_view.size)
        self.assertEqual(3, record_map_view.upper)
        self.assertEqual(0, record_map_view.lower)
        self.assertEqual(new_item, record_map_view.get_item(1))
        self.assertEqual(3, record_map_view.record.item_count)
        self.assertEqual(2, record_map_view.record.field_count)
        self.assertEqual(0, record_map_view.record.flags)
        self.assertEqual(None, record_map_view.record.fields)

    def test_record_map_view_add_none_index(self):
        # Given
        record = Record.create()
        record.add(Attr.create_attr('B', 'H'))
        record.add(Attr.create_attr('E', 'R'))
        new_item = Text.create_from('Foo')
        record_map_view = RecordMapView(record, 1, 2)
        # When
        actual_response = record_map_view.add(new_item)
        # Then
        self.assertTrue(actual_response)
        self.assertEqual(2, record_map_view.size)
        self.assertEqual(3, record_map_view.upper)
        self.assertEqual(1, record_map_view.lower)
        self.assertEqual(new_item, record_map_view.get_item(1))

    def test_record_map_view_branch_empty(self):
        # Given
        record = Record.create()
        record.add(Attr.create_attr('Q', 'H'))
        record.add(Attr.create_attr('W', 'R'))
        record_map_view = RecordMapView(record, 0, 0)
        # When
        actual = record_map_view.branch()
        # Then
        self.assertEqual(0, actual.size)
        self.assertEqual(0, actual.field_count)
        self.assertIsInstance(actual, RecordMap)
        self.assertNotEqual(record_map_view.record.items, actual.items)
        self.assertEqual([], actual.items)
        self.assertEqual(None, actual.fields)

    def test_record_map_view_branch_single(self):
        # Given
        record = Record.create()
        first = Attr.create_attr('R', 'H')
        second = Attr.create_attr('Y', 'R')
        record.add(first)
        record.add(second)
        record_map_view = RecordMapView(record, 0, 1)
        # When
        actual = record_map_view.branch()
        # Then
        self.assertEqual(1, actual.size)
        self.assertEqual(1, actual.field_count)
        self.assertIsInstance(actual, RecordMap)
        self.assertNotEqual(record_map_view.record.items, actual.items)
        self.assertEqual([first], actual.items)
        self.assertEqual(None, actual.fields)

    def test_record_map_view_branch_multiple_fields(self):
        # Given
        record = Record.create()
        first = Attr.create_attr('T', 'H')
        second = Attr.create_attr('E', 'R')
        third = Attr.create_attr('P', 'Q')
        record.add(first)
        record.add(second)
        record.add(third)
        record_map_view = RecordMapView(record, 0, 2)
        # When
        actual = record_map_view.branch()
        # Then
        self.assertEqual(2, actual.size)
        self.assertEqual(2, actual.field_count)
        self.assertIsInstance(actual, RecordMap)
        self.assertNotEqual(record_map_view.record.items, actual.items)
        self.assertEqual([first, second], actual.items)
        self.assertEqual(None, actual.fields)

    def test_record_map_view_branch_multiple_values(self):
        # Given
        record = Record.create()
        second = Text.create_from('Bar')
        third = Text.create_from('Baz')
        fourth = Text.create_from('Qux')
        record.add(Text.create_from('Foo'))
        record.add(second)
        record.add(third)
        record.add(fourth)
        record_map_view = RecordMapView(record, 1, 4)
        # When
        actual = record_map_view.branch()
        # Then
        self.assertEqual(3, actual.size)
        self.assertEqual(0, actual.field_count)
        self.assertIsInstance(actual, RecordMap)
        self.assertNotEqual(record_map_view.record.items, actual.items)
        self.assertEqual([second, third, fourth], actual.items)
        self.assertEqual(None, actual.fields)

    def test_record_map_view_branch_multiple_values_and_fields(self):
        # Given
        record = Record.create()
        first = Text.create_from('Bar')
        second = Attr.create_attr('E', 'R')
        third = Text.create_from('Baz')
        fourth = Attr.create_attr('P', 'Q')
        record.add(first)
        record.add(second)
        record.add(third)
        record.add(fourth)
        record_map_view = RecordMapView(record, 0, 3)
        # When
        actual = record_map_view.branch()
        # Then
        self.assertEqual(3, actual.size)
        self.assertEqual(1, actual.field_count)
        self.assertIsInstance(actual, RecordMap)
        self.assertNotEqual(record_map_view.record.items, actual.items)
        self.assertEqual([first, second, third], actual.items)
        self.assertEqual(None, actual.fields)

    def test_value_builder_add_field_to_empty_record(self):
        # Given
        value_builder = ValueBuilder()
        item = Attr.create_attr('Foo', 'Boo')
        # When
        actual_response = value_builder.add(item)
        # Then
        self.assertTrue(actual_response)
        self.assertEqual(1, value_builder.record.size)
        self.assertEqual(None, value_builder.value)

    def test_value_builder_add_field_existing_record(self):
        # Given
        value_builder = ValueBuilder()
        value_builder.add(Attr.create_attr('Baz', 'Qux'))
        item = Attr.create_attr('Foo', 'Boo')
        # When
        actual_response = value_builder.add(item)
        # Then
        self.assertTrue(actual_response)
        self.assertEqual(2, value_builder.record.size)
        self.assertEqual(None, value_builder.value)

    def test_value_builder_add_field_to_empty_record_and_existing_value(self):
        # Given
        value_builder = ValueBuilder()
        value_builder.add(Text.create_from('Baz'))
        item = Attr.create_attr('Moo', 'Cow')
        # When
        actual_response = value_builder.add(item)
        # Then
        self.assertTrue(actual_response)
        self.assertEqual(2, value_builder.record.size)
        self.assertEqual(None, value_builder.value)
        self.assertIsInstance(value_builder.record.get_item(0), Text)
        self.assertIsInstance(value_builder.record.get_item(1), Attr)

    def test_value_builder_add_value_to_existing_record(self):
        # Given
        value_builder = ValueBuilder()
        value_builder.add(Attr.create_attr('Moo', 'Cow'))
        value_builder.add(Attr.create_attr('Boo', 'Ghost'))
        item = Text.create_from('Baz')
        # When
        actual_response = value_builder.add(item)
        # Then
        self.assertTrue(actual_response)
        self.assertEqual(3, value_builder.record.size)
        self.assertEqual(None, value_builder.value)
        self.assertIsInstance(value_builder.record.get_item(0), Attr)
        self.assertIsInstance(value_builder.record.get_item(1), Attr)
        self.assertIsInstance(value_builder.record.get_item(2), Text)

    def test_value_builder_add_value_to_empty_record_and_value(self):
        # Given
        value_builder = ValueBuilder()
        item = Text.create_from('Bar')
        # When
        actual_response = value_builder.add(item)
        # Then
        self.assertTrue(actual_response)
        self.assertEqual(None, value_builder.record)
        self.assertEqual('Bar', value_builder.value.value)

    def test_value_builder_add_value_to_empty_record_exiting_value(self):
        # Given
        value_builder = ValueBuilder()
        value_builder.add(Text.create_from('Bar'))
        value_builder.add(Text.create_from('Boo'))
        value_builder.add(Text.create_from('Foo'))
        item = Text.create_from('Moo')
        # When
        actual_response = value_builder.add(item)
        # Then
        self.assertTrue(actual_response)
        self.assertEqual(4, value_builder.record.size)
        self.assertEqual(None, value_builder.value)
        self.assertIsInstance(value_builder.record.get_item(0), Text)
        self.assertIsInstance(value_builder.record.get_item(1), Text)

    def test_value_builder_add_not_supported(self):
        # Given
        value_builder = ValueBuilder()
        item = CustomItem()
        # When
        with self.assertRaises(TypeError) as error:
            value_builder.add(item)
        # Then
        message = error.exception.args[0]
        self.assertEqual(f'Item of type CustomItem is not supported by the Value Builder', message)

    def test_value_builder_bind_with_record(self):
        # Given
        value_builder = ValueBuilder()
        attr = Attr.create_attr('Foo', 'Bar')
        value_builder.add(attr)
        # When
        actual = value_builder.bind()
        # Then
        self.assertIsInstance(actual, RecordMap)
        self.assertEqual(1, actual.size)
        self.assertEqual(attr, actual.get_item(0))

    def test_value_builder_bind_with_value(self):
        # Given
        value_builder = ValueBuilder()
        value = Text.create_from('Foo')
        value_builder.add(value)
        # When
        actual = value_builder.bind()
        # Then
        self.assertEqual(value, actual)

    def test_value_builder_bind_with_empty_record_and_value(self):
        # Given
        value_builder = ValueBuilder()
        # When
        actual = value_builder.bind()
        # Then
        self.assertEqual(Absent.get_absent(), actual)
