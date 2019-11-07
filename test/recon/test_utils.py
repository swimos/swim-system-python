import unittest

from aiounittest import async_test
from swimai.recon import ReconUtils, OutputMessage
from test.utils import CustomString


class TestUtils(unittest.TestCase):

    @async_test
    async def test_is_valid_ident_start_char_A(self):
        # Given
        character = 'A'
        # When
        actual = await ReconUtils.is_ident_start_char(character)
        # Then
        self.assertTrue(actual)

    @async_test
    async def test_is_valid_ident_start_char_Z(self):
        # Given
        character = 'Z'
        # When
        actual = await ReconUtils.is_ident_start_char(character)
        # Then
        self.assertTrue(actual)

    @async_test
    async def test_is_valid_ident_start_char_P(self):
        # Given
        character = 'P'
        # When
        actual = await ReconUtils.is_ident_start_char(character)
        # Then
        self.assertTrue(actual)

    @async_test
    async def test_is_valid_ident_start_char_a(self):
        # Given
        character = 'a'
        # When
        actual = await ReconUtils.is_ident_start_char(character)
        # Then
        self.assertTrue(actual)

    @async_test
    async def test_is_valid_ident_start_char_z(self):
        # Given
        character = 'z'
        # When
        actual = await ReconUtils.is_ident_start_char(character)
        # Then
        self.assertTrue(actual)

    @async_test
    async def test_is_valid_ident_start_char_h(self):
        # Given
        character = 'h'
        # When
        actual = await ReconUtils.is_ident_start_char(character)
        # Then
        self.assertTrue(actual)

    @async_test
    async def test_is_valid_ident_start_char_underscore(self):
        # Given
        character = '_'
        # When
        actual = await ReconUtils.is_ident_start_char(character)
        # Then
        self.assertTrue(actual)

    @async_test
    async def test_is_invalid_ident_start_char_digit(self):
        # Given
        character = '4'
        # When
        actual = await ReconUtils.is_ident_start_char(character)
        # Then
        self.assertFalse(actual)

    @async_test
    async def test_is_invalid_ident_start_char_hyphen(self):
        # Given
        character = '-'
        # When
        actual = await ReconUtils.is_ident_start_char(character)
        # Then
        self.assertFalse(actual)

    @async_test
    async def test_is_invalid_ident_start_char_dollar(self):
        # Given
        character = '$'
        # When
        actual = await ReconUtils.is_ident_start_char(character)
        # Then
        self.assertFalse(actual)

    @async_test
    async def test_is_invalid_ident_start_char_empty(self):
        # Given
        character = ''
        # When
        actual = await ReconUtils.is_ident_start_char(character)
        # Then
        self.assertFalse(actual)

    @async_test
    async def test_is_valid_ident_char_A(self):
        # Given
        character = 'A'
        # When
        actual = await ReconUtils.is_ident_char(character)
        # Then
        self.assertTrue(actual)

    @async_test
    async def test_is_valid_ident_char_Z(self):
        # Given
        character = 'Z'
        # When
        actual = await ReconUtils.is_ident_char(character)
        # Then
        self.assertTrue(actual)

    @async_test
    async def test_is_valid_ident_char_N(self):
        # Given
        character = 'N'
        # When
        actual = await ReconUtils.is_ident_char(character)
        # Then
        self.assertTrue(actual)

    @async_test
    async def test_is_valid_ident_char_a(self):
        # Given
        character = 'a'
        # When
        actual = await ReconUtils.is_ident_char(character)
        # Then
        self.assertTrue(actual)

    @async_test
    async def test_is_valid_ident_char_z(self):
        # Given
        character = 'z'
        # When
        actual = await ReconUtils.is_ident_char(character)
        # Then
        self.assertTrue(actual)

    @async_test
    async def test_is_valid_ident_char_g(self):
        # Given
        character = 'g'
        # When
        actual = await ReconUtils.is_ident_char(character)
        # Then
        self.assertTrue(actual)

    @async_test
    async def test_is_valid_ident_char_underscore(self):
        # Given
        character = '_'
        # When
        actual = await ReconUtils.is_ident_char(character)
        # Then
        self.assertTrue(actual)

    @async_test
    async def test_is_valid_ident_char_hyphen(self):
        # Given
        character = '-'
        # When
        actual = await ReconUtils.is_ident_char(character)
        # Then
        self.assertTrue(actual)

    @async_test
    async def test_is_valid_ident_char_0(self):
        # Given
        character = '0'
        # When
        actual = await ReconUtils.is_ident_char(character)
        # Then
        self.assertTrue(actual)

    @async_test
    async def test_is_valid_ident_char_9(self):
        # Given
        character = '9'
        # When
        actual = await ReconUtils.is_ident_char(character)
        # Then
        self.assertTrue(actual)

    @async_test
    async def test_is_valid_ident_char_5(self):
        # Given
        character = '5'
        # When
        actual = await ReconUtils.is_ident_char(character)
        # Then
        self.assertTrue(actual)

    @async_test
    async def test_is_invalid_ident_char_dollar(self):
        # Given
        character = '$'
        # When
        actual = await ReconUtils.is_ident_char(character)
        # Then
        self.assertFalse(actual)

    @async_test
    async def test_is_invalid_ident_char_empty(self):
        # Given
        character = ''
        # When
        actual = await ReconUtils.is_ident_char(character)
        # Then
        self.assertFalse(actual)

    @async_test
    async def test_is_valid_ident(self):
        # Given
        value = 'test1'
        # When
        actual = await ReconUtils.is_ident(value)
        # Then
        self.assertTrue(actual)

    @async_test
    async def test_is_invalid_ident_empty(self):
        # Given
        value = ''
        # When
        actual = await ReconUtils.is_ident(value)
        # Then
        self.assertFalse(actual)

    @async_test
    async def test_is_invalid_ident_invalid_start_char(self):
        # Given
        value = '1test'
        # When
        actual = await ReconUtils.is_ident(value)
        # Then
        self.assertFalse(actual)

    @async_test
    async def test_is_invalid_ident_invalid_middle_char(self):
        # Given
        value = 'test$test'
        # When
        actual = await ReconUtils.is_ident(value)
        # Then
        self.assertFalse(actual)

    @async_test
    async def test_is_invalid_ident_invalid_end_char(self):
        # Given
        value = 'test$'
        # When
        actual = await ReconUtils.is_ident(value)
        # Then
        self.assertFalse(actual)

    @async_test
    async def test_is_invalid_ident_invalid_all_chars(self):
        # Given
        value = '^%&*'
        # When
        actual = await ReconUtils.is_ident(value)
        # Then
        self.assertFalse(actual)

    @async_test
    async def test_is_valid_space_char_space(self):
        # Given
        character = ' '
        # When
        actual = await ReconUtils.is_space(character)
        # Then
        self.assertTrue(actual)

    @async_test
    async def test_is_valid_space_char_tab(self):
        # Given
        character = '\t'
        # When
        actual = await ReconUtils.is_space(character)
        # Then
        self.assertTrue(actual)

    @async_test
    async def test_is_invalid_space_char_digit(self):
        # Given
        character = '5'
        # When
        actual = await ReconUtils.is_space(character)
        # Then
        self.assertFalse(actual)

    @async_test
    async def test_is_invalid_space_char_letter(self):
        # Given
        character = 'l'
        # When
        actual = await ReconUtils.is_space(character)
        # Then
        self.assertFalse(actual)

    @async_test
    async def test_is_invalid_space_char_empty(self):
        # Given
        character = ''
        # When
        actual = await ReconUtils.is_space(character)
        # Then
        self.assertFalse(actual)

    @async_test
    async def test_is_valid_digit_char_1(self):
        # Given
        character = '2'
        # When
        actual = await ReconUtils.is_digit(character)
        # Then
        self.assertTrue(actual)

    @async_test
    async def test_is_valid_digit_char_0(self):
        # Given
        character = '0'
        # When
        actual = await ReconUtils.is_digit(character)
        # Then
        self.assertTrue(actual)

    @async_test
    async def test_is_valid_digit_char_7(self):
        # Given
        character = '7'
        # When
        actual = await ReconUtils.is_digit(character)
        # Then
        self.assertTrue(actual)

    @async_test
    async def test_is_valid_digit_char_9(self):
        # Given
        character = '9'
        # When
        actual = await ReconUtils.is_digit(character)
        # Then
        self.assertTrue(actual)

    @async_test
    async def test_is_invalid_digit_char_letter(self):
        # Given
        character = 'b'
        # When
        actual = await ReconUtils.is_digit(character)
        # Then
        self.assertFalse(actual)

    @async_test
    async def test_is_invalid_digit_char_underscore(self):
        # Given
        character = '_'
        # When
        actual = await ReconUtils.is_digit(character)
        # Then
        self.assertFalse(actual)

    @async_test
    async def test_is_invalid_digit_char_empty(self):
        # Given
        character = ''
        # When
        actual = await ReconUtils.is_digit(character)
        # Then
        self.assertFalse(actual)

    @async_test
    async def test_to_ord_str(self):
        # Given
        character = 'p'
        # When
        actual = await ReconUtils.to_ord(character)
        # Then
        self.assertEqual(112, actual)

    @async_test
    async def test_to_ord_int(self):
        # Given
        character = 3
        # When
        actual = await ReconUtils.to_ord(character)
        # Then
        self.assertEqual(3, actual)

    @async_test
    async def test_to_ord_other(self):
        # Given
        character = 3.12
        # When
        actual = await ReconUtils.to_ord(character)
        # Then
        self.assertEqual(None, actual)

    @async_test
    async def test_output_message_create_empty(self):
        # Given
        chars = None
        # When
        actual = await OutputMessage.create(chars)
        # Then
        self.assertIsInstance(actual, OutputMessage)
        self.assertEqual('', actual.value)
        self.assertEqual(0, actual.size)
        self.assertEqual('', actual.last_char)

    @async_test
    async def test_output_message_create_single(self):
        # Given
        chars = 'p'
        # When
        actual = await OutputMessage.create(chars)
        # Then
        self.assertIsInstance(actual, OutputMessage)
        self.assertEqual('p', actual.value)
        self.assertEqual(1, actual.size)
        self.assertEqual('p', actual.last_char)

    @async_test
    async def test_output_message_create_multiple(self):
        # Given
        chars = 'foo_bar'
        # When
        actual = await OutputMessage.create(chars)
        # Then
        self.assertIsInstance(actual, OutputMessage)
        self.assertEqual('foo_bar', actual.value)
        self.assertEqual(7, actual.size)
        self.assertEqual('r', actual.last_char)

    @async_test
    async def test_output_message_append_str_to_empty(self):
        # Given
        output_message = await OutputMessage.create('')
        chars = 'bar'
        # When
        await output_message.append(chars)
        # Then
        self.assertIsInstance(output_message, OutputMessage)
        self.assertEqual('bar', output_message.value)
        self.assertEqual(3, output_message.size)
        self.assertEqual('r', output_message.last_char)

    @async_test
    async def test_output_message_append_float_to_empty(self):
        # Given
        output_message = await OutputMessage.create('')
        chars = 21.12
        # When
        await output_message.append(chars)
        # Then
        self.assertIsInstance(output_message, OutputMessage)
        self.assertEqual('21.12', output_message.value)
        self.assertEqual(5, output_message.size)
        self.assertEqual('2', output_message.last_char)

    @async_test
    async def test_output_message_append_int_to_empty(self):
        # Given
        output_message = await OutputMessage.create('')
        chars = 13
        # When
        await output_message.append(chars)
        # Then
        self.assertIsInstance(output_message, OutputMessage)
        self.assertEqual('13', output_message.value)
        self.assertEqual(2, output_message.size)
        self.assertEqual('3', output_message.last_char)

    @async_test
    async def test_output_message_append_output_message_to_empty(self):
        # Given
        output_message = await OutputMessage.create('')
        chars = await OutputMessage.create('boo_fast')
        # When
        await output_message.append(chars)
        # Then
        self.assertIsInstance(output_message, OutputMessage)
        self.assertEqual('boo_fast', output_message.value)
        self.assertEqual(8, output_message.size)
        self.assertEqual('t', output_message.last_char)

    @async_test
    async def test_output_message_append_invalid_to_empty(self):
        # Given
        output_message = await OutputMessage.create('')
        chars = CustomString('moo')
        # When
        with self.assertRaises(TypeError) as error:
            await output_message.append(chars)
        # Then
        message = error.exception.args[0]
        self.assertEqual(f'Item of type CustomString cannot be added to the OutputMessage!', message)

    @async_test
    async def test_output_message_append_str_to_existing(self):
        # Given
        output_message = await OutputMessage.create('full')
        chars = '_qux'
        # When
        await output_message.append(chars)
        # Then
        self.assertIsInstance(output_message, OutputMessage)
        self.assertEqual('full_qux', output_message.value)
        self.assertEqual(8, output_message.size)
        self.assertEqual('x', output_message.last_char)

    @async_test
    async def test_output_message_append_float_to_existing(self):
        # Given
        output_message = await OutputMessage.create('full')
        chars = 22.1
        # When
        await output_message.append(chars)
        # Then
        self.assertIsInstance(output_message, OutputMessage)
        self.assertEqual('full22.1', output_message.value)
        self.assertEqual(8, output_message.size)
        self.assertEqual('1', output_message.last_char)

    @async_test
    async def test_output_message_append_int_to_existing(self):
        # Given
        output_message = await OutputMessage.create('empty')
        chars = 73
        # When
        await output_message.append(chars)
        # Then
        self.assertIsInstance(output_message, OutputMessage)
        self.assertEqual('empty73', output_message.value)
        self.assertEqual(7, output_message.size)
        self.assertEqual('3', output_message.last_char)

    @async_test
    async def test_output_message_append_output_message_to_existing(self):
        # Given
        output_message = await OutputMessage.create('empty')
        chars = await OutputMessage.create(' house')
        # When
        await output_message.append(chars)
        # Then
        self.assertIsInstance(output_message, OutputMessage)
        self.assertEqual('empty house', output_message.value)
        self.assertEqual(11, output_message.size)
        self.assertEqual('e', output_message.last_char)

    @async_test
    async def test_output_message_append_invalid_to_existing(self):
        # Given
        output_message = await OutputMessage.create('bar')
        chars = CustomString('foo')
        # When
        with self.assertRaises(TypeError) as error:
            await output_message.append(chars)
        # Then
        message = error.exception.args[0]
        self.assertEqual(f'Item of type CustomString cannot be added to the OutputMessage!', message)

    def test_input_message_head_empty(self):
        pass

    def test_input_message_head_continuous(self):
        pass

    def test_input_message_head_not_continuous(self):
        pass

    def test_step_message_once(self):
        pass

    def test_step_message_twice(self):
        pass

    def test_step_message_out_of_bound(self):
        pass

    def test_step_all(self):
        pass

    def test_is_cont_empty(self):
        pass

    def test_is_cont_existing(self):
        pass
