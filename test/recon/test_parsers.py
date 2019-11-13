import unittest

from aiounittest import async_test

from swimai.recon import ReconParser, InputMessage, OutputMessage
from swimai.recon.parsers import DecimalParser
from swimai.structures import RecordMap, Slot, Text, Attr, Absent, Num, Extant, Bool


class TestParsers(unittest.TestCase):

    @async_test
    async def test_parse_literal_slot_empty_builder(self):
        # Given
        message = await InputMessage.create('{foo: bar}')
        parser = ReconParser()
        # When
        actual = await parser.parse_literal(message)
        # Then
        self.assertIsInstance(actual, RecordMap)
        self.assertIsInstance(actual, RecordMap)
        self.assertIsInstance(actual.get_item(0), Slot)
        self.assertIsInstance(actual.get_item(0).key, Text)
        self.assertEqual('foo', actual.get_item(0).key.value)
        self.assertIsInstance(actual.get_item(0).value, Text)
        self.assertEqual('bar', actual.get_item(0).value.value)

    @async_test
    async def test_parse_literal_slot_existing_builder(self):
        # Given
        message = await InputMessage.create('{Foo: Bar}')
        builder = await ReconParser.create_value_builder()
        builder.add(Attr.create_attr('Baz', 'Qux'))
        parser = ReconParser()
        # When
        actual = await parser.parse_literal(message, builder)
        # Then
        self.assertIsInstance(actual, RecordMap)
        self.assertEqual(2, actual.size)
        self.assertIsInstance(actual.get_item(0), Attr)
        self.assertIsInstance(actual.get_item(0).key, Text)
        self.assertEqual('Baz', actual.get_item(0).key.value)
        self.assertIsInstance(actual.get_item(0).value, str)
        self.assertEqual('Qux', actual.get_item(0).value)
        self.assertIsInstance(actual.get_item(1), Slot)
        self.assertIsInstance(actual.get_item(1).key, Text)
        self.assertEqual('Foo', actual.get_item(1).key.value)
        self.assertIsInstance(actual.get_item(1).value, Text)
        self.assertEqual('Bar', actual.get_item(1).value.value)

    @async_test
    async def test_parse_literal_ident_empty_builder(self):
        # Given
        message = await InputMessage.create('foo')
        parser = ReconParser()
        # When
        actual = await parser.parse_literal(message)
        # Then
        self.assertIsInstance(actual, Text)
        self.assertEqual('foo', actual.value)
        self.assertEqual(Absent.get_absent(), actual.key)

    @async_test
    async def test_parse_literal_ident_existing_builder(self):
        # Given
        message = await InputMessage.create('foo')
        builder = await ReconParser.create_value_builder()
        builder.add(Text.create_from('bar'))
        parser = ReconParser()
        # When
        actual = await parser.parse_literal(message, builder)
        # Then
        self.assertIsInstance(actual, RecordMap)
        self.assertEqual(2, actual.size)
        self.assertIsInstance(actual.get_item(0), Text)
        self.assertIsInstance(actual.get_item(1), Text)
        self.assertEqual('bar', actual.get_item(0).value)
        self.assertEqual('foo', actual.get_item(1).value)

    @async_test
    async def test_parse_literal_quote_empty_builder(self):
        # Given
        message = await InputMessage.create('"Baz_Foo"')
        parser = ReconParser()
        # When
        actual = await parser.parse_literal(message)
        # Then
        self.assertIsInstance(actual, Text)
        self.assertIsInstance(actual.value, str)
        self.assertEqual('Baz_Foo', actual.value)

    @async_test
    async def test_parse_literal_quote_existing_builder(self):
        # Given
        message = await InputMessage.create('"Hello_World"')
        builder = await ReconParser.create_value_builder()
        parser = ReconParser()
        builder.add(Text.create_from('Hi'))
        builder.add(Text.create_from('Bye'))
        # When
        actual = await parser.parse_literal(message, builder)
        # Then
        self.assertIsInstance(actual, RecordMap)
        self.assertEqual(3, actual.size)
        self.assertIsInstance(actual.get_item(0), Text)
        self.assertIsInstance(actual.get_item(1), Text)
        self.assertIsInstance(actual.get_item(2), Text)
        self.assertEqual('Hi', actual.get_item(0).value)
        self.assertEqual('Bye', actual.get_item(1).value)
        self.assertEqual('Hello_World', actual.get_item(2).value)

    @async_test
    async def test_parse_literal_minus_empty_builder(self):
        # Given
        message = await InputMessage.create('-13.42')
        parser = ReconParser()
        # When
        actual = await parser.parse_literal(message)
        # Then
        self.assertIsInstance(actual, Num)
        self.assertIsInstance(actual.value, float)
        self.assertEqual(-13.42, actual.value)

    @async_test
    async def test_parse_literal_minus_existing_builder(self):
        # Given
        message = await InputMessage.create('  37')
        parser = ReconParser()
        builder = await ReconParser.create_value_builder()
        builder.add(Text.create_from('Hello'))
        builder.add(Text.create_from('Friend'))
        # When
        actual = await parser.parse_literal(message, builder)
        # Then
        self.assertEqual(3, actual.size)
        self.assertIsInstance(actual, RecordMap)
        self.assertIsInstance(actual.get_item(0), Text)
        self.assertIsInstance(actual.get_item(1), Text)
        self.assertIsInstance(actual.get_item(2), Num)
        self.assertEqual('Hello', actual.get_item(0).value)
        self.assertEqual('Friend', actual.get_item(1).value)
        self.assertEqual(37, actual.get_item(2).value)

    @async_test
    async def test_parse_literal_empty_empty_builder(self):
        # Given
        message = await InputMessage.create('')
        parser = ReconParser()
        # When
        actual = await parser.parse_literal(message)
        # Then
        self.assertEqual(Absent.get_absent(), actual)

    @async_test
    async def test_parse_literal_empty_existing_builder(self):
        # Given
        message = await InputMessage.create('')
        builder = await ReconParser.create_value_builder()
        builder.add(Text.create_from('Hello'))
        parser = ReconParser()
        # When
        actual = await parser.parse_literal(message, builder)
        # Then
        self.assertIsInstance(actual, Text)
        self.assertEqual(0, actual.size)
        self.assertEqual('Hello', actual.value)

    @async_test
    async def test_parse_decimal_positive_empty_value(self):
        # Given
        message = await InputMessage.create('.32')
        parser = ReconParser()
        # When
        actual = await DecimalParser.parse(message, parser)
        # Then
        self.assertIsInstance(actual, Num)
        self.assertEqual(0.32, actual.value)

    @async_test
    async def test_parse_decimal_positive_existing_value(self):
        # Given
        message = await InputMessage.create('.691')
        parser = ReconParser()
        value_output = 12
        # When
        actual = await DecimalParser.parse(message, parser, value_output)
        # Then
        self.assertIsInstance(actual, Num)
        self.assertEqual(12.691, actual.value)

    @async_test
    async def test_parse_decimal_negative_empty_value(self):
        # Given
        message = await InputMessage.create('.1')
        parser = ReconParser()
        # When
        actual = await DecimalParser.parse(message, parser, sign_output=-1)
        # Then
        self.assertIsInstance(actual, Num)
        self.assertEqual(-0.1, actual.value)

    @async_test
    async def test_parse_decimal_negative_existing_value(self):
        # Given
        message = await InputMessage.create('.1091')
        parser = ReconParser()
        value_output = -13
        # When
        actual = await DecimalParser.parse(message, parser, value_output, sign_output=-1)
        # Then
        self.assertIsInstance(actual, Num)
        self.assertEqual(-13.1091, actual.value)

    @async_test
    async def test_parse_decimal_empty_positive_empty_value(self):
        # Given
        message = await InputMessage.create('')
        parser = ReconParser()
        # When
        actual = await DecimalParser.parse(message, parser)
        # Then
        self.assertIsInstance(actual, Num)
        self.assertEqual(0.0, actual.value)

    @async_test
    async def test_parse_decimal_empty_positive_existing_value(self):
        # Given
        message = await InputMessage.create('')
        parser = ReconParser()
        value_output = 15
        # When
        actual = await DecimalParser.parse(message, parser, value_output)
        # Then
        self.assertIsInstance(actual, Num)
        self.assertEqual(15.0, actual.value)

    @async_test
    async def test_parse_decimal_empty_negative_empty_value(self):
        # Given
        message = await InputMessage.create('')
        parser = ReconParser()
        # When
        actual = await DecimalParser.parse(message, parser, sign_output=-1)
        # Then
        self.assertIsInstance(actual, Num)
        self.assertEqual(-0.0, actual.value)

    @async_test
    async def test_parse_decimal_empty_negative_existing_value(self):
        # Given
        message = await InputMessage.create('')
        parser = ReconParser()
        value_output = -16
        # When
        actual = await DecimalParser.parse(message, parser, value_output, sign_output=-1)
        # Then
        self.assertIsInstance(actual, Num)
        self.assertEqual(-16.0, actual.value)

    @async_test
    async def test_parse_decimal_dot_only_positive_empty_value(self):
        # Given
        message = await InputMessage.create('.')
        parser = ReconParser()
        # When
        actual = await DecimalParser.parse(message, parser)
        # Then
        self.assertIsInstance(actual, Num)
        self.assertEqual(0.0, actual.value)

    @async_test
    async def test_parse_decimal_dot_only_positive_existing_value(self):
        # Given
        message = await InputMessage.create('.')
        parser = ReconParser()
        value_output = 17
        # When
        actual = await DecimalParser.parse(message, parser, value_output)
        # Then
        self.assertIsInstance(actual, Num)
        self.assertEqual(17.0, actual.value)

    @async_test
    async def test_parse_decimal_dot_only_negative_empty_value(self):
        # Given
        message = await InputMessage.create('.')
        parser = ReconParser()
        # When
        actual = await DecimalParser.parse(message, parser, sign_output=-1)
        # Then
        self.assertIsInstance(actual, Num)
        self.assertEqual(-0.0, actual.value)

    @async_test
    async def test_parse_decimal_dot_only_negative_existing_value(self):
        # Given
        message = await InputMessage.create('.')
        parser = ReconParser()
        value_output = -18
        # When
        actual = await DecimalParser.parse(message, parser, value_output, sign_output=-1)
        # Then
        self.assertIsInstance(actual, Num)
        self.assertEqual(-18.0, actual.value)

    @async_test
    async def test_parse_number_positive_int(self):
        # Given
        message = await InputMessage.create(' 112')
        parser = ReconParser()
        # When
        actual = await parser.parse_number(message)
        # Then
        self.assertIsInstance(actual, Num)
        self.assertEqual(112, actual.value)

    @async_test
    async def test_parse_number_negative_int(self):
        # Given
        message = await InputMessage.create('-90')
        parser = ReconParser()
        # When
        actual = await parser.parse_number(message)
        # Then
        self.assertIsInstance(actual, Num)
        self.assertEqual(-90, actual.value)

    @async_test
    async def test_parse_number_positive_float_full(self):
        # Given
        message = await InputMessage.create('91.11')
        parser = ReconParser()
        # When
        actual = await parser.parse_number(message)
        # Then
        self.assertIsInstance(actual, Num)
        self.assertEqual(91.11, actual.value)

    @async_test
    async def test_parse_number_negative_float_full(self):
        # Given
        message = await InputMessage.create('  -11.12')
        parser = ReconParser()
        # When
        actual = await parser.parse_number(message)
        # Then
        self.assertIsInstance(actual, Num)
        self.assertEqual(-11.12, actual.value)

    @async_test
    async def test_parse_number_positive_float_decimal_only(self):
        # Given
        message = await InputMessage.create('  .12')
        parser = ReconParser()
        # When
        actual = await parser.parse_number(message)
        # Then
        self.assertIsInstance(actual, Num)
        self.assertEqual(0.12, actual.value)

    @async_test
    async def test_parse_number_negative_float_decimal_only(self):
        # Given
        message = await InputMessage.create('  .31')
        parser = ReconParser()
        # When
        actual = await parser.parse_number(message, sign_output=-1)
        # Then
        self.assertIsInstance(actual, Num)
        self.assertEqual(-0.31, actual.value)

    @async_test
    async def test_parse_number_float_point_only(self):
        # Given
        message = await InputMessage.create('.')
        parser = ReconParser()
        # When
        actual = await parser.parse_number(message, sign_output=-1)
        # Then
        self.assertIsInstance(actual, Num)
        self.assertEqual(-0.00, actual.value)

    @async_test
    async def test_parse_number_empty(self):
        # Given
        message = await InputMessage.create('')
        parser = ReconParser()
        # When
        actual = await parser.parse_number(message)
        # Then
        self.assertIsInstance(actual, Num)
        self.assertEqual(0, actual.value)

    @async_test
    async def test_parse_number_leading_zero(self):
        # Given
        message = await InputMessage.create('012')
        parser = ReconParser()
        # When
        actual = await parser.parse_number(message)
        # Then
        self.assertIsInstance(actual, Num)
        self.assertEqual(12, actual.value)

    @async_test
    async def test_parse_number_leading_zeroes(self):
        # Given
        message = await InputMessage.create('00013')
        parser = ReconParser()
        # When
        actual = await parser.parse_number(message)
        # Then
        self.assertIsInstance(actual, Num)
        self.assertEqual(13, actual.value)

    @async_test
    async def test_parse_string_normal(self):
        # Given
        message = await InputMessage.create('"Hello, friend"')
        parser = ReconParser()
        # When
        actual = await parser.parse_string(message)
        # Then
        self.assertIsInstance(actual, Text)
        self.assertEqual('Hello, friend', actual.value)

    @async_test
    async def test_parse_string_missing_closing_quote(self):
        # Given
        message = await InputMessage.create('  "Hello, World')
        parser = ReconParser()
        # When
        actual = await parser.parse_string(message)
        # Then
        self.assertIsInstance(actual, Text)
        self.assertEqual('Hello, World', actual.value)

    @async_test
    async def test_parse_string_existing_output(self):
        # Given
        message = await InputMessage.create('"dog"')
        output = await OutputMessage.create('This is ')
        parser = ReconParser()
        # When
        actual = await parser.parse_string(message, output)
        # Then
        self.assertIsInstance(actual, Text)
        self.assertEqual('This is dog', actual.value)

    @async_test
    async def test_parse_string_empty(self):
        # Given
        message = InputMessage()
        parser = ReconParser()
        # When
        actual = await parser.parse_string(message)
        # Then
        self.assertIsInstance(actual, Text)
        self.assertEqual('', actual.value)

    @async_test
    async def test_parse_ident_valid(self):
        # Given
        message = await InputMessage.create('test')
        parser = ReconParser()
        # When
        actual = await parser.parse_ident(message)
        # Then
        self.assertIsInstance(actual, Text)
        self.assertEqual('test', actual.value)

    @async_test
    async def test_parse_ident_valid_with_leading_spaces(self):
        # Given
        message = await InputMessage.create('   foo')
        parser = ReconParser()
        # When
        actual = await parser.parse_ident(message)
        # Then
        self.assertIsInstance(actual, Text)
        self.assertEqual('foo', actual.value)

    @async_test
    async def test_parse_ident_valid_with_output(self):
        # Given
        message = await InputMessage.create('   foo')
        parser = ReconParser()
        output = await OutputMessage.create('bar_')
        # When
        actual = await parser.parse_ident(message, output)
        # Then
        self.assertIsInstance(actual, Text)
        self.assertEqual('bar_foo', actual.value)

    @async_test
    async def test_parse_ident_invalid_with_output(self):
        # Given
        message = await InputMessage.create('$$')
        parser = ReconParser()
        output = await OutputMessage.create('hello')
        # When
        actual = await parser.parse_ident(message, output)
        # Then
        self.assertIsInstance(actual, Text)
        self.assertEqual('hello', actual.value)

    @async_test
    async def test_parse_ident_invalid(self):
        # Given
        message = await InputMessage.create('$lane: test')
        parser = ReconParser()
        # When
        with self.assertRaises(TypeError) as error:
            await parser.parse_ident(message)
        # Then
        message = error.exception.args[0]
        self.assertEqual('Identifier starting at position 0 is invalid!\nMessage: $lane: test', message)

    @async_test
    async def test_parse_ident_empty(self):
        # Given
        message = await InputMessage.create('')
        parser = ReconParser()
        # When
        with self.assertRaises(TypeError) as error:
            await parser.parse_ident(message)
        # Then
        message = error.exception.args[0]
        self.assertEqual('Identifier starting at position 0 is invalid!\nMessage: ', message)

    @async_test
    async def test_parse_attr_no_body(self):
        # Given
        message = await InputMessage.create('@animal')
        parser = ReconParser()
        # When
        actual = await parser.parse_attr(message)
        # Then
        self.assertIsInstance(actual, Attr)
        self.assertIsInstance(actual.key, Text)
        self.assertEqual('animal', actual.key.value)

    @async_test
    async def test_parse_attr_slot_key_only(self):
        # Given
        message = await InputMessage.create('@animal(node)')
        parser = ReconParser()
        # When
        actual = await parser.parse_attr(message)
        # Then
        self.assertIsInstance(actual, Attr)
        self.assertIsInstance(actual.key, Text)
        self.assertEqual('animal', actual.key.value)
        self.assertIsInstance(actual.value, RecordMap)
        self.assertEqual(1, actual.value.size)
        self.assertIsInstance(actual.value.get_item(0), Slot)
        self.assertEqual('node', actual.value.get_item(0).key.value)
        self.assertEqual(Extant.get_extant(), actual.value.get_item(0).value)

    @async_test
    async def test_parse_attr_slot_key_and_value(self):
        # Given
        message = await InputMessage.create('@vehicle(car: red)')
        parser = ReconParser()
        # When
        actual = await parser.parse_attr(message)
        # Then
        self.assertIsInstance(actual, Attr)
        self.assertIsInstance(actual.key, Text)
        self.assertEqual('vehicle', actual.key.value)
        self.assertEqual(1, actual.value.size)
        self.assertIsInstance(actual.value, RecordMap)
        self.assertIsInstance(actual.value.get_item(0), Slot)
        self.assertEqual('car', actual.value.get_item(0).key.value)
        self.assertEqual('red', actual.value.get_item(0).value.value)

    @async_test
    async def test_parse_attr_existing_key_and_value(self):
        # Given
        message = await InputMessage.create('')
        parser = ReconParser()
        key_output = Text.create_from('Baz')
        value_output = Text.create_from('Qux')
        # When
        actual = await parser.parse_attr(message, key_output, value_output)
        # Then
        self.assertIsInstance(actual, Attr)
        self.assertIsInstance(actual.key, Text)
        self.assertIsInstance(actual.value, Text)
        self.assertEqual('Baz', actual.key.value)
        self.assertEqual('Qux', actual.value.value)

    @async_test
    async def test_parse_attr_empty(self):
        # Given
        message = await InputMessage.create('')
        parser = ReconParser()
        # When
        with self.assertRaises(TypeError) as error:
            await parser.parse_attr(message)
        # Then
        message = error.exception.args[0]
        self.assertEqual('Attribute starting at position 0 is invalid!\nMessage: ', message)

    @async_test
    async def test_attr_expression_parser_parse_attribute(self):
        # Given
        message = await InputMessage.create('@test')
        parser = ReconParser()
        # When
        actual = await parser.parse_attr_expression(message)
        # Then
        self.assertIsInstance(actual, RecordMap)
        self.assertEqual(1, actual.size)
        self.assertEqual('test', actual.tag)

    @async_test
    async def test_attr_expression_parser_parse_attribute_existing_field(self):
        # Given
        message = await InputMessage.create('@test')
        parser = ReconParser()
        builder = RecordMap.create()
        builder.add(Text.create_from('Moo'))
        field = Text.create_from('Boo')
        # When
        actual = await parser.parse_attr_expression(message, builder=builder, field_output=field)
        # Then
        self.assertIsInstance(actual, RecordMap)
        self.assertEqual(3, actual.size)
        self.assertEqual('Moo', actual.get_item(0).value)
        self.assertEqual('Boo', actual.get_item(1).value)
        self.assertEqual('test', actual.get_item(2).key.value)

    @async_test
    async def test_attr_expression_parser_parse_literal(self):
        # Given
        message = await InputMessage.create('literal')
        parser = ReconParser()
        # When
        actual = await parser.parse_attr_expression(message)
        # Then
        self.assertIsInstance(actual, Text)
        self.assertEqual('literal', actual.value)

    @async_test
    async def test_attr_expression_parser_parse_literal_existing_value(self):
        # Given
        message = await InputMessage.create('literal')
        parser = ReconParser()
        builder = RecordMap.create()
        builder.add(Text.create_from('Moo'))
        value = Text.create_from('Dog')
        # When
        actual = await parser.parse_attr_expression(message, builder=builder, value_output=value)
        # Then
        self.assertIsInstance(actual, RecordMap)
        self.assertEqual(3, actual.size)
        self.assertEqual('Moo', actual.get_item(0).value)
        self.assertEqual('Dog', actual.get_item(1).value)
        self.assertEqual('literal', actual.get_item(2).value)

    @async_test
    async def test_attr_expression_parser_parse_record_curly_brackets(self):
        # Given
        message = await InputMessage.create('{record}')
        parser = ReconParser()
        # When
        actual = await parser.parse_attr_expression(message)
        # Then
        self.assertIsInstance(actual, RecordMap)
        self.assertEqual(1, actual.size)
        self.assertEqual('record', actual.get_item(0).key.value)

    @async_test
    async def test_attr_expression_parser_parse_record_square_brackets(self):
        # Given
        message = await InputMessage.create('[record]')
        parser = ReconParser()
        # When
        actual = await parser.parse_attr_expression(message)
        # Then
        self.assertIsInstance(actual, RecordMap)
        self.assertEqual(1, actual.size)
        self.assertEqual('record', actual.get_item(0).key.value)

    @async_test
    async def test_record_parser_parse_single(self):
        # Given
        message = await InputMessage.create('{animal: dog}')
        parser = ReconParser()
        # When
        actual = await parser.parse_record(message)
        # Then
        self.assertIsInstance(actual, RecordMap)
        self.assertEqual(1, actual.size)
        self.assertEqual('animal', actual.get_item(0).key.value)
        self.assertEqual('dog', actual.get_item(0).value.value)

    @async_test
    async def test_record_parser_parse_double(self):
        # Given
        message = await InputMessage.create('{cat: meow, dog: bark}')
        parser = ReconParser()
        # When
        actual = await parser.parse_record(message)
        # Then
        self.assertIsInstance(actual, RecordMap)
        self.assertEqual(2, actual.size)
        self.assertEqual('cat', actual.get_item(0).key.value)
        self.assertEqual('meow', actual.get_item(0).value.value)
        self.assertEqual('dog', actual.get_item(1).key.value)
        self.assertEqual('bark', actual.get_item(1).value.value)

    @async_test
    async def test_record_parser_parse_multiple(self):
        # Given
        message = await InputMessage.create('{dog: bark,  bird: chirp , cat  : meow }')
        parser = ReconParser()
        # When
        actual = await parser.parse_record(message)
        # Then
        self.assertIsInstance(actual, RecordMap)
        self.assertEqual(3, actual.size)
        self.assertEqual('dog', actual.get_item(0).key.value)
        self.assertEqual('bark', actual.get_item(0).value.value)
        self.assertEqual('bird', actual.get_item(1).key.value)
        self.assertEqual('chirp', actual.get_item(1).value.value)
        self.assertEqual('cat', actual.get_item(2).key.value)
        self.assertEqual('meow', actual.get_item(2).value.value)

    @async_test
    async def test_record_parser_parse_square_brackets(self):
        # Given
        message = await InputMessage.create('[pet: mouse]')
        parser = ReconParser()
        # When
        actual = await parser.parse_record(message)
        # Then
        self.assertIsInstance(actual, RecordMap)
        self.assertEqual(1, actual.size)
        self.assertEqual('pet', actual.get_item(0).key.value)
        self.assertEqual('mouse', actual.get_item(0).value.value)

    @async_test
    async def test_record_parser_parse_no_brackets(self):
        # Given
        message = await InputMessage.create('duck: quack, dog: bark')
        parser = ReconParser()
        # When
        actual = await parser.parse_record(message)
        # Then
        self.assertIsInstance(actual, RecordMap)
        self.assertEqual(2, actual.size)
        self.assertEqual('duck', actual.get_item(0).key.value)
        self.assertEqual('quack', actual.get_item(0).value.value)
        self.assertEqual('dog', actual.get_item(1).key.value)
        self.assertEqual('bark', actual.get_item(1).value.value)

    @async_test
    async def test_record_parser_parse_semicolon_delimiter(self):
        # Given
        message = await InputMessage.create('{large_dog: collie ; small_dog: pug}')
        parser = ReconParser()
        # When
        actual = await parser.parse_record(message)
        # Then
        self.assertIsInstance(actual, RecordMap)
        self.assertEqual(2, actual.size)
        self.assertEqual('large_dog', actual.get_item(0).key.value)
        self.assertEqual('collie', actual.get_item(0).value.value)
        self.assertEqual('small_dog', actual.get_item(1).key.value)
        self.assertEqual('pug', actual.get_item(1).value.value)

    @async_test
    async def test_record_parser_parse_missing_closing_bracket(self):
        # Given
        message = await InputMessage.create('{hello: world, bye: world')
        parser = ReconParser()
        # When
        actual = await parser.parse_record(message)
        # Then
        self.assertIsInstance(actual, RecordMap)
        self.assertEqual(2, actual.size)
        self.assertEqual('hello', actual.get_item(0).key.value)
        self.assertEqual('world', actual.get_item(0).value.value)
        self.assertEqual('bye', actual.get_item(1).key.value)
        self.assertEqual('world', actual.get_item(1).value.value)

    @async_test
    async def test_record_parser_parse_missing_opening_bracket(self):
        # Given
        message = await InputMessage.create('bye: world, hello: world}')
        parser = ReconParser()
        # When
        actual = await parser.parse_record(message)
        # Then
        self.assertIsInstance(actual, RecordMap)
        self.assertEqual(2, actual.size)
        self.assertEqual('bye', actual.get_item(0).key.value)
        self.assertEqual('world', actual.get_item(0).value.value)
        self.assertEqual('hello', actual.get_item(1).key.value)
        self.assertEqual('world', actual.get_item(1).value.value)

    @async_test
    async def test_record_parser_parse_key_only(self):
        # Given
        message = await InputMessage.create('{foo}')
        parser = ReconParser()
        # When
        actual = await parser.parse_record(message)
        # Then
        self.assertIsInstance(actual, RecordMap)
        self.assertEqual(1, actual.size)
        self.assertIsInstance(actual.get_item(0), Slot)
        self.assertEqual('foo', actual.get_item(0).key.value)

    @async_test
    async def test_record_parser_parse_existing_key_empty(self):
        # Given
        message = await InputMessage.create('')
        parser = ReconParser()
        key = Text.create_from('dog')
        # When
        actual = await parser.parse_record(message, key_output=key)
        # Then
        self.assertIsInstance(actual, RecordMap)
        self.assertEqual(1, actual.size)
        self.assertIsInstance(actual.get_item(0), Slot)
        self.assertEqual('dog', actual.get_item(0).key.value)

    @async_test
    async def test_record_parser_parse_existing_key_value(self):
        # Given
        message = await InputMessage.create(':dog')
        parser = ReconParser()
        key = Text.create_from('animal')
        # When
        actual = await parser.parse_record(message, key_output=key)
        # Then
        self.assertIsInstance(actual, RecordMap)
        self.assertEqual(1, actual.size)
        self.assertEqual('animal', actual.get_item(0).key.value)
        self.assertEqual('dog', actual.get_item(0).value.value)

    @async_test
    async def test_record_parser_parse_existing_key_multiple(self):
        # Given
        message = await InputMessage.create(':dog, test:bar')
        parser = ReconParser()
        key = Text.create_from('animal')
        # When
        actual = await parser.parse_record(message, key_output=key)
        # Then
        self.assertIsInstance(actual, RecordMap)
        self.assertEqual(2, actual.size)
        self.assertEqual('animal', actual.get_item(0).key.value)
        self.assertEqual('dog', actual.get_item(0).value.value)
        self.assertEqual('test', actual.get_item(1).key.value)
        self.assertEqual('bar', actual.get_item(1).value.value)

    @async_test
    async def test_record_parser_parse_existing_value_multiple(self):
        # Given
        message = await InputMessage.create('animal, test:foo')
        parser = ReconParser()
        value = Text.create_from('cat')
        # When
        actual = await parser.parse_record(message, value_output=value)
        # Then
        self.assertIsInstance(actual, RecordMap)
        self.assertEqual(2, actual.size)
        self.assertEqual('animal', actual.get_item(0).key.value)
        self.assertEqual('cat', actual.get_item(0).value.value)
        self.assertEqual('test', actual.get_item(1).key.value)
        self.assertEqual('foo', actual.get_item(1).value.value)

    @async_test
    async def test_record_parser_parse_existing_builder_empty(self):
        # Given
        message = await InputMessage.create('')
        parser = ReconParser()
        builder = await parser.create_record_builder()
        builder.add(await parser.create_slot(Text.create_from('cow'), Text.create_from('moo')))
        # When
        actual = await parser.parse_record(message, builder=builder)
        # Then
        self.assertIsInstance(actual, RecordMap)
        self.assertEqual(1, actual.size)
        self.assertEqual('cow', actual.get_item(0).key.value)
        self.assertEqual('moo', actual.get_item(0).value.value)

    @async_test
    async def test_record_parser_parse_existing_builder_single(self):
        # Given
        message = await InputMessage.create(' cat: meow')
        parser = ReconParser()
        builder = await parser.create_record_builder()
        builder.add(await parser.create_slot(Text.create_from('dog'), Text.create_from('bark')))
        # When
        actual = await parser.parse_record(message, builder=builder)
        # Then
        self.assertIsInstance(actual, RecordMap)
        self.assertEqual(2, actual.size)
        self.assertEqual('dog', actual.get_item(0).key.value)
        self.assertEqual('bark', actual.get_item(0).value.value)
        self.assertEqual('cat', actual.get_item(1).key.value)
        self.assertEqual('meow', actual.get_item(1).value.value)

    @async_test
    async def test_record_parser_parse_existing_builder_multiple(self):
        # Given
        message = await InputMessage.create(' pig: oink')
        parser = ReconParser()
        builder = await parser.create_record_builder()
        builder.add(await parser.create_slot(Text.create_from('bird'), Text.create_from('chirp')))
        builder.add(await parser.create_slot(Text.create_from('dog'), Text.create_from('bark')))
        # When
        actual = await parser.parse_record(message, builder=builder)
        # Then
        self.assertIsInstance(actual, RecordMap)
        self.assertEqual(3, actual.size)
        self.assertEqual('bird', actual.get_item(0).key.value)
        self.assertEqual('chirp', actual.get_item(0).value.value)
        self.assertEqual('dog', actual.get_item(1).key.value)
        self.assertEqual('bark', actual.get_item(1).value.value)
        self.assertEqual('pig', actual.get_item(2).key.value)
        self.assertEqual('oink', actual.get_item(2).value.value)

    @async_test
    async def test_record_parser_parse_empty(self):
        # Given
        message = await InputMessage.create('')
        parser = ReconParser()
        # When
        actual = await parser.parse_record(message)
        # Then
        self.assertIsInstance(actual, RecordMap)
        self.assertEqual(0, actual.size)
        self.assertEqual(Absent.get_absent(), actual.value)

    @async_test
    async def test_record_parser_parse_block_string(self):
        # Given
        message = '@animals{dog: bark  , cat: meow; bird : chirp}'
        parser = ReconParser()
        # When
        actual = await parser.parse_block_string(message)
        # Then
        self.assertIsInstance(actual, RecordMap)
        self.assertEqual(4, actual.size)
        self.assertEqual('animals', actual.tag)
        self.assertEqual('dog', actual.get_item(1).key.value)
        self.assertEqual('bark', actual.get_item(1).value.value)
        self.assertEqual('cat', actual.get_item(2).key.value)
        self.assertEqual('meow', actual.get_item(2).value.value)
        self.assertEqual('bird', actual.get_item(3).key.value)
        self.assertEqual('chirp', actual.get_item(3).value.value)

    @async_test
    async def test_create_ident_true(self):
        # Given
        message = 'true'
        # When
        actual = await ReconParser.create_ident(message)
        # Then
        self.assertIsInstance(actual, Bool)
        self.assertEqual(True, actual.value)

    @async_test
    async def test_create_ident_false(self):
        # Given
        message = 'false'
        # When
        actual = await ReconParser.create_ident(message)
        # Then
        self.assertIsInstance(actual, Bool)
        self.assertEqual(False, actual.value)

    @async_test
    async def test_create_ident_text(self):
        # Given
        message = 'Dog'
        # When
        actual = await ReconParser.create_ident(message)
        # Then
        self.assertIsInstance(actual, Text)
        self.assertEqual('Dog', actual.value)
