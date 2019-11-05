import unittest

from aiounittest import async_test
from swimai import Recon, RecordMap, Attr, Text, Slot
from swimai.recon.parsers import ReconStructureParser
from swimai.recon.writers import ReconStructureWriter


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
        # Given
        value = RecordMap.create()
        value.add(Attr.create_attr(Text.create_from('remove'),
                                   RecordMap.create_record_map(
                                       Slot.create_slot(Text.create_from('key'), Text.create_from('foo')))))
        # When
        actual = await Recon.to_string(value)
        # Then
        self.assertEqual('@remove(key:foo)', actual)

    def test_get_structure_writer_once(self):
        # When
        actual = Recon.get_structure_writer()
        # Then
        self.assertIsInstance(actual, ReconStructureWriter)
        self.assertEqual(Recon.get_structure_writer(), actual)

    def test_get_structure_writer_multiple(self):
        # Given
        expected = Recon.get_structure_writer()
        # When
        actual = Recon.get_structure_writer()
        # Then
        self.assertIsInstance(actual, ReconStructureWriter)
        self.assertEqual(expected, actual)
        self.assertEqual(Recon.get_structure_writer(), actual)

    def get_structure_parser_once(self):
        # When
        actual = Recon.get_structure_parser()
        # Then
        self.assertIsInstance(actual, ReconStructureParser)
        self.assertEqual(Recon.get_structure_parser(), actual)

    def get_structure_parser_multiple(self):
        # Given
        expected = Recon.get_structure_parser()
        # When
        actual = Recon.get_structure_parser()
        # Then
        self.assertIsInstance(actual, ReconStructureParser)
        self.assertEqual(expected, actual)
        self.assertEqual(Recon.get_structure_parser(), actual)