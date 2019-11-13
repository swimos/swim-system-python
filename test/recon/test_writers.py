import unittest

from aiounittest import async_test

from swimai.recon import OutputMessage
from swimai.recon.writers import BoolWriter, IdentWriter, NumberWriter, StringWriter, SlotWriter, ReconWriter, \
    AttrWriter, BlockWriter
from swimai.structures import Text, Slot, Record, Extant, Attr


class TestWriters(unittest.TestCase):

    @async_test
    async def test_ident_writer_str(self):
        # Given
        message = 'hello'
        # When
        actual = await IdentWriter.write(message)
        # Then
        self.assertIsInstance(actual, OutputMessage)
        self.assertEqual('hello', actual.value)

    @async_test
    async def test_ident_writer_empty(self):
        # Given
        message = ''
        # When
        actual = await IdentWriter.write(message)
        # Then
        self.assertIsInstance(actual, OutputMessage)
        self.assertEqual('', actual.value)

    @async_test
    async def test_bool_writer_true(self):
        # Given
        message = True
        # When
        actual = await BoolWriter.write(message)
        # Then
        self.assertIsInstance(actual, OutputMessage)
        self.assertEqual('true', actual.value)

    @async_test
    async def test_bool_writer_false(self):
        # Given
        message = False
        # When
        actual = await BoolWriter.write(message)
        # Then
        self.assertIsInstance(actual, OutputMessage)
        self.assertEqual('false', actual.value)

    @async_test
    async def test_bool_writer_none(self):
        # Given
        message = None
        # When
        actual = await BoolWriter.write(message)
        # Then
        self.assertIsInstance(actual, OutputMessage)
        self.assertEqual('false', actual.value)

    @async_test
    async def test_number_writer_int(self):
        # Given
        message = 25
        # When
        actual = await NumberWriter.write(message)
        # Then
        self.assertIsInstance(actual, OutputMessage)
        self.assertEqual('25', actual.value)

    @async_test
    async def test_number_writer_float(self):
        # Given
        message = 0.02
        # When
        actual = await NumberWriter.write(message)
        # Then
        self.assertIsInstance(actual, OutputMessage)
        self.assertEqual('0.02', actual.value)

    @async_test
    async def test_number_writer_none(self):
        # Given
        message = None
        # When
        actual = await NumberWriter.write(message)
        # Then
        self.assertIsInstance(actual, OutputMessage)
        self.assertEqual('', actual.value)

    @async_test
    async def test_string_writer_str(self):
        # Given
        message = 'This is dog'
        # When
        actual = await StringWriter.write(message)
        # Then
        self.assertIsInstance(actual, OutputMessage)
        self.assertEqual('"This is dog"', actual.value)

    @async_test
    async def test_string_writer_empty(self):
        # Given
        message = None
        # When
        actual = await StringWriter.write(message)
        # Then
        self.assertIsInstance(actual, OutputMessage)
        self.assertEqual('""', actual.value)

    @async_test
    async def test_slot_writer_existing_key_and_value(self):
        # Given
        key = Text.create_from('animal')
        value = Text.create_from('dog')
        writer = ReconWriter()
        # When
        actual = await SlotWriter.write(key=key, writer=writer, value=value)
        # Then
        self.assertIsInstance(actual, OutputMessage)
        self.assertEqual('animal:dog', actual.value)

    @async_test
    async def test_slot_writer_existing_key_missing_value(self):
        # Given
        key = Text.create_from('animal')
        writer = ReconWriter()
        # When
        actual = await SlotWriter.write(key=key, writer=writer)
        # Then
        self.assertIsInstance(actual, OutputMessage)
        self.assertEqual('animal:', actual.value)

    @async_test
    async def test_slot_writer_missing_key_existing_value(self):
        # Given
        value = Text.create_from('dog')
        writer = ReconWriter()
        # When
        actual = await SlotWriter.write(value=value, writer=writer)
        # Then
        self.assertIsInstance(actual, OutputMessage)
        self.assertEqual(':dog', actual.value)

    @async_test
    async def test_slot_writer_missing_key_and_value(self):
        # Given
        writer = ReconWriter()
        # When
        actual = await SlotWriter.write(writer=writer)
        # Then
        self.assertIsInstance(actual, OutputMessage)
        self.assertEqual(':', actual.value)

    @async_test
    async def test_attr_writer_existing_key_and_value_text(self):
        # Given
        key = Text.create_from('bird')
        value = Text.create_from('chirp')
        writer = ReconWriter()
        # When
        actual = await AttrWriter.write(key=key, writer=writer, value=value)
        # Then
        self.assertIsInstance(actual, OutputMessage)
        self.assertEqual('@bird(chirp)', actual.message)

    @async_test
    async def test_attr_writer_existing_key_and_value_slot(self):
        # Given
        key = Text.create_from('animal')
        value = Record.create()
        value.add(Slot.create_slot(Text.create_from('dog'), Text.create_from('bark')))
        writer = ReconWriter()
        # When
        actual = await AttrWriter.write(key=key, writer=writer, value=value)
        # Then
        self.assertIsInstance(actual, OutputMessage)
        self.assertEqual('@animal(dog:bark)', actual.message)

    @async_test
    async def test_attr_writer_missing_key_existing_value(self):
        # Given
        value = Text.create_from('chirp')
        writer = ReconWriter()
        # When
        actual = await AttrWriter.write(writer=writer, value=value)
        # Then
        self.assertIsInstance(actual, OutputMessage)
        self.assertEqual('@(chirp)', actual.message)

    @async_test
    async def test_attr_writer_existing_key_missing_value(self):
        # Given
        key = Text.create_from('bird')
        writer = ReconWriter()
        # When
        actual = await AttrWriter.write(key=key, writer=writer)
        # Then
        self.assertIsInstance(actual, OutputMessage)
        self.assertEqual('@bird', actual.message)

    @async_test
    async def test_attr_writer_existing_key_extant_value(self):
        # Given
        key = Text.create_from('bird')
        value = Extant.get_extant()
        writer = ReconWriter()
        # When
        actual = await AttrWriter.write(key=key, writer=writer, value=value)
        # Then
        self.assertIsInstance(actual, OutputMessage)
        self.assertEqual('@bird', actual.message)

    @async_test
    async def test_attr_writer_missing_key_and_value(self):
        # Given
        writer = ReconWriter()
        # When
        actual = await AttrWriter.write(writer=writer)
        # Then
        self.assertIsInstance(actual, OutputMessage)
        self.assertEqual('@', actual.message)

    @async_test
    async def test_block_writer_attr(self):
        # Given
        items = list()
        items.append(Attr.create_attr(Text.create_from('dog'), Text.create_from('bark')))
        writer = ReconWriter()
        # When
        actual = await BlockWriter.write(items, writer=writer)
        # Then
        self.assertIsInstance(actual, OutputMessage)
        self.assertEqual('@dog(bark)', actual.message)

    @async_test
    async def test_block_writer_text_single(self):
        # Given
        items = list()
        items.append(Text.create_from('Dead parrot'))
        writer = ReconWriter()
        # When
        actual = await BlockWriter.write(items, writer=writer)
        # Then
        self.assertIsInstance(actual, OutputMessage)
        self.assertEqual('"Dead parrot"', actual.message)

    @async_test
    async def test_block_writer_text_multiple(self):
        # Given
        items = list()
        items.append(Text.create_from('foo_'))
        items.append(Text.create_from('bar'))
        writer = ReconWriter()
        # When
        actual = await BlockWriter.write(items, writer=writer)
        # Then
        self.assertIsInstance(actual, OutputMessage)
        self.assertEqual('foo_bar', actual.message)

    @async_test
    async def test_block_writer_slot_single_first(self):
        # Given
        items = list()
        items.append(Slot.create_slot(Text.create_from('cat'), Text.create_from('meow')))
        writer = ReconWriter()
        # When
        actual = await BlockWriter.write(items, writer=writer, first=True)
        # Then
        self.assertIsInstance(actual, OutputMessage)
        self.assertEqual('cat:meow', actual.message)

    @async_test
    async def test_block_writer_slot_single_not_first(self):
        # Given
        items = list()
        items.append(Slot.create_slot(Text.create_from('cat'), Text.create_from('meow')))
        writer = ReconWriter()
        # When
        actual = await BlockWriter.write(items, writer=writer, first=False)
        # Then
        self.assertIsInstance(actual, OutputMessage)
        self.assertEqual(',cat:meow', actual.message)

    @async_test
    async def test_block_writer_slot_multiple(self):
        # Given
        items = list()
        items.append(Slot.create_slot(Text.create_from('dog'), Text.create_from('bark')))
        items.append(Slot.create_slot(Text.create_from('cat'), Text.create_from('meow')))
        writer = ReconWriter()
        # When
        actual = await BlockWriter.write(items, writer=writer, first=True)
        # Then
        self.assertIsInstance(actual, OutputMessage)
        self.assertEqual('dog:bark,cat:meow', actual.message)

    @async_test
    async def test_block_writer_slot_in_attr(self):
        # Given
        items = list()
        record_map = Record.create()
        record_map.add(Slot.create_slot(Text.create_from('cat'), Text.create_from('meow')))
        items.append(Attr.create_attr(Text.create_from('animal'), record_map))
        writer = ReconWriter()
        # When
        actual = await BlockWriter.write(items, writer=writer, first=True)
        # Then
        self.assertIsInstance(actual, OutputMessage)
        self.assertEqual('@animal(cat:meow)', actual.message)

    @async_test
    async def test_block_writer_slot_in_attr_and_slot(self):
        # Given
        items = list()
        record_map = Record.create()
        record_map.add(Slot.create_slot(Text.create_from('dog'), Text.create_from('bark')))
        items.append(Attr.create_attr(Text.create_from('animal'), record_map))
        items.append(Slot.create_slot(Text.create_from('cat'), Text.create_from('meow')))
        writer = ReconWriter()
        # When
        actual = await BlockWriter.write(items, writer=writer, first=True)
        # Then
        self.assertIsInstance(actual, OutputMessage)
        self.assertEqual('@animal(dog:bark){cat:meow}', actual.message)

    @async_test
    async def test_block_writer_multiple_attributes(self):
        # Given
        items = list()

        record_map = Record.create()

        dog_map = Record.create()
        dog_map.add(Slot.create_slot(Text.create_from('dog'), Text.create_from('bark')))
        record_map.add(Attr.create_attr(Text.create_from('Animal'), dog_map))

        cat_map = Record.create()
        cat_map.add(Slot.create_slot(Text.create_from('cat'), Text.create_from('meow')))
        record_map.add(Attr.create_attr(Text.create_from('Animal'), cat_map))

        bird_map = Record.create()
        bird_map.add(Slot.create_slot(Text.create_from('bird'), Text.create_from('chirp')))
        record_map.add(Attr.create_attr(Text.create_from('Animal'), bird_map))

        items.append(record_map)

        writer = ReconWriter()
        # When
        actual = await BlockWriter.write(items, writer=writer, first=True)
        # Then
        self.assertIsInstance(actual, OutputMessage)
        self.assertEqual('@Animal(dog:bark)@Animal(cat:meow)@Animal(bird:chirp)', actual.message)

    @async_test
    async def test_block_writer_nested_attributes(self):
        # Given
        items = list()
        name_record = Record.create()
        name_record.add(Slot.create_slot(Text.create_from('Name'), Text.create_from('Collie')))
        breed_record = Record.create()
        breed_record.add(Attr.create_attr(Text.create_from('Breed'), name_record))
        dog_record = Record.create()
        dog_record.add(Slot.create_slot(Text.create_from('Dog'), breed_record))
        species_record = Record.create()
        species_record.add(Attr.create_attr(Text.create_from('Species'), dog_record))
        animals_record = Record.create()
        animals_record.add(Slot.create_slot(Text.create_from('Animals'), species_record))
        items.append(Attr.create_attr(Text.create_from('Zoo'), animals_record))
        writer = ReconWriter()
        # When
        actual = await BlockWriter.write(items, writer=writer, first=True)
        # Then
        self.assertIsInstance(actual, OutputMessage)
        self.assertEqual('@Zoo(Animals:@Species(Dog:@Breed(Name:Collie)))', actual.message)

        pass

    @async_test
    async def test_block_writer_empty(self):
        # Given
        items = list()
        writer = ReconWriter()
        # When
        actual = await BlockWriter.write(items, writer=writer)
        # Then
        self.assertIsInstance(actual, OutputMessage)
        self.assertEqual('', actual.message)
