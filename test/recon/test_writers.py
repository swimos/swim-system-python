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

import unittest

from aiounittest import async_test

from swimai.recon import OutputMessage
from swimai.recon.writers import BoolWriter, IdentWriter, NumberWriter, StringWriter, SlotWriter, ReconWriter, \
    AttrWriter, BlockWriter
from swimai.structures import Text, Slot, Record, Extant, Attr, Num, Bool, Absent
from test.utils import CustomItem


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
    async def test_number_writer_zero(self):
        # Given
        message = 0
        # When
        actual = await NumberWriter.write(message)
        # Then
        self.assertIsInstance(actual, OutputMessage)
        self.assertEqual('0', actual.value)

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

    @async_test
    async def test_write_record_single(self):
        # Given
        record = Record.create()
        record.add(Text.create_from('Dog'))
        writer = ReconWriter()
        # When
        actual = await writer.write_record(record)
        # Then
        self.assertIsInstance(actual, OutputMessage)
        self.assertEqual(3, actual.size)
        self.assertEqual('Dog', actual.value)
        self.assertEqual('g', actual.last_char)

    @async_test
    async def test_write_record_multiple(self):
        # Given
        record = Record.create()
        record.add(Text.create_from('Dog'))
        record.add(Text.create_from('Cat'))
        writer = ReconWriter()
        # When
        actual = await writer.write_record(record)
        # Then
        self.assertIsInstance(actual, OutputMessage)
        self.assertEqual(6, actual.size)
        self.assertEqual('DogCat', actual.value)
        self.assertEqual('t', actual.last_char)

    @async_test
    async def test_write_record_empty(self):
        # Given
        record = Record.create()
        writer = ReconWriter()
        # When
        actual = await writer.write_record(record)
        # Then
        self.assertIsNone(actual)

    @async_test
    async def test_write_value_record(self):
        # Given
        record = Record.create()
        record.add(Slot.create_slot(Text.create_from('Cow'), Text.create_from('Moo')))
        writer = ReconWriter()
        # When
        actual = await writer.write_value(record)
        # Then
        self.assertIsInstance(actual, OutputMessage)
        self.assertEqual(7, actual.size)
        self.assertEqual('Cow:Moo', actual.value)
        self.assertEqual('o', actual.last_char)

    @async_test
    async def test_write_value_text_ident(self):
        # Given
        ident = Text.create_from('Duck')
        writer = ReconWriter()
        # When
        actual = await writer.write_value(ident)
        # Then
        self.assertIsInstance(actual, OutputMessage)
        self.assertEqual(4, actual.size)
        self.assertEqual('Duck', actual.value)
        self.assertEqual('k', actual.last_char)

    @async_test
    async def test_write_value_text_string(self):
        # Given
        string = Text.create_from('$duck')
        writer = ReconWriter()
        # When
        actual = await writer.write_value(string)
        # Then
        self.assertIsInstance(actual, OutputMessage)
        self.assertEqual(7, actual.size)
        self.assertEqual('"$duck"', actual.value)
        self.assertEqual('"', actual.last_char)

    @async_test
    async def test_write_value_number(self):
        # Given
        number = Num.create_from(-13.1)
        writer = ReconWriter()
        # When
        actual = await writer.write_value(number)
        # Then
        self.assertIsInstance(actual, OutputMessage)
        self.assertEqual(5, actual.size)
        self.assertEqual('-13.1', actual.value)
        self.assertEqual('1', actual.last_char)

    @async_test
    async def test_write_value_bool(self):
        # Given
        boolean = Bool.create_from(False)
        writer = ReconWriter()
        # When
        actual = await writer.write_value(boolean)
        # Then
        self.assertIsInstance(actual, OutputMessage)
        self.assertEqual(5, actual.size)
        self.assertEqual('false', actual.value)
        self.assertEqual('e', actual.last_char)

    @async_test
    async def test_write_value_absent(self):
        # Given
        absent = Absent.get_absent()
        writer = ReconWriter()
        # When
        actual = await writer.write_value(absent)
        # Then
        self.assertIsInstance(actual, OutputMessage)
        self.assertEqual(0, actual.size)
        self.assertEqual('', actual.value)

    @async_test
    async def test_write_slot(self):
        # Given
        key = Text.create_from('Hello')
        value = Text.create_from('Friend')
        writer = ReconWriter()
        # When
        actual = await writer.write_slot(key, value)
        # Then
        self.assertIsInstance(actual, OutputMessage)
        self.assertEqual(12, actual.size)
        self.assertEqual('Hello:Friend', actual.value)
        self.assertEqual('d', actual.last_char)

    @async_test
    async def test_write_attr(self):
        # Given
        key = Text.create_from('Hello')
        value = Text.create_from('Friend')
        writer = ReconWriter()
        # When
        actual = await writer.write_attr(key, value)
        # Then
        self.assertIsInstance(actual, OutputMessage)
        self.assertEqual(14, actual.size)
        self.assertEqual('@Hello(Friend)', actual.value)
        self.assertEqual(')', actual.last_char)

    @async_test
    async def test_write_item_attr(self):
        # Given
        item = Attr.create_attr(Text.create_from('Cat'), Text.create_from('Meow'))
        writer = ReconWriter()
        # When
        actual = await writer.write_item(item)
        # Then
        self.assertIsInstance(actual, str)
        self.assertEqual('@Cat(Meow)', actual)

    @async_test
    async def test_write_item_slot(self):
        # Given
        item = Slot.create_slot(Text.create_from('Age'), Num.create_from(32))
        writer = ReconWriter()
        # When
        actual = await writer.write_item(item)
        # Then
        self.assertIsInstance(actual, str)
        self.assertEqual('Age:32', actual)

    @async_test
    async def test_write_item_value(self):
        # Given
        item = Text.create_from('Horse#')
        writer = ReconWriter()
        # When
        actual = await writer.write_item(item)
        # Then
        self.assertIsInstance(actual, str)
        self.assertEqual('"Horse#"', actual)

    @async_test
    async def test_write_item_invalid(self):
        # Given
        item = CustomItem()
        writer = ReconWriter()
        # When
        with self.assertRaises(TypeError) as error:
            await writer.write_item(item)

        # Then
        message = error.exception.args[0]
        self.assertEqual('No Recon serialization for CustomItem!', message)
