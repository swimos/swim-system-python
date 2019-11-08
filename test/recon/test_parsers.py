import unittest

from aiounittest import async_test

from swimai.recon import ReconParser, InputMessage
from swimai.structures import RecordMap, Slot, Text


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
        # message = await InputMessage.create('{foo: bar}')
        # parser = ReconParser()
        # When
        # actual = await parser.parse_literal(message)
        # Then
        # pass
        pass

    @async_test
    async def test_parse_literal_ident_empty_builder(self):
        # Given
        message = await InputMessage.create('foo')
        parser = ReconParser()
        # When
        actual = await parser.parse_literal(message)
        # Then
        pass

    @async_test
    async def test_parse_literal_ident_existing_builder(self):
        # Given
        # message = await InputMessage.create('foo')
        # parser = ReconParser()
        # When
        # actual = await parser.parse_literal(message)
        # Then
        pass

    @async_test
    async def test_parse_literal_quote_empty_builder(self):
        # Given
        message = await InputMessage.create('"bar"')
        parser = ReconParser()
        # When
        actual = await parser.parse_literal(message)
        # Then
        pass

    @async_test
    async def test_parse_literal_quote_existing_builder(self):
        # # Given
        # message = await InputMessage.create('"bar"')
        # parser = ReconParser()
        # # When
        # actual = await parser.parse_literal(message)
        # # Then
        pass

    @async_test
    async def test_parse_literal_minus_empty_builder(self):
        # # Given
        # message = await InputMessage.create('"bar"')
        # parser = ReconParser()
        # # When
        # actual = await parser.parse_literal(message)
        # # Then
        pass
