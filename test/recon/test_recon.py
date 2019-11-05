import unittest

from aiounittest import async_test

from swimai import Recon, RecordMap


class TestRecon(unittest.TestCase):

    @async_test
    async def test_parse(self):
        # Given
        recon_string = '@sync(node: "foo/node", lane: "foo/lane")"Hello, World"'
        # When
        actual = await Recon.parse(recon_string)
        # Then
        self.assertIsInstance(actual, RecordMap)
        self.assertEqual('sync', actual.tag)
        self.assertEqual(2, actual.size)
        self.assertEqual('foo/node', actual.get_item(0).value.get_item(0).value.value)
        self.assertEqual('foo/lane', actual.get_item(0).value.get_item(1).value.value)
        self.assertEqual('Hello, World', actual.get_item(1).value)

    @async_test
    async def test_to_string(self):
        pass

    def test_get_structure_writer_once(self):
        pass

    def test_get_structure_writer_multiple(self):
        pass

    def get_structure_parser_once(self):
        pass

    def get_structure_parser_multiple(self):
        pass
