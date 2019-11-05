import unittest

from aiounittest import async_test
from swimai.recon.utils import ReconUtils


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
