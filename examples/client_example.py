# Setting the value of a value lane on a remote agent.
import time

from examples.person import Person, Pet
from swimai import SwimClient
from swimai.structures import Text, Num, Slot, Attr, RecordMap, Extant


async def my_custom_callback_correct(new_value, old_value):
    print(f'New: {new_value}')
    print(f'Old: {old_value}')


def my_custom_exception_callback():
    print('custom exception callback')


with SwimClient(strict=False) as swim_client:
    host_uri = 'ws://localhost:9001'
    node_uri = '/unit/foo'

    # swim_client.register_class(Person)
    # swim_client.register_class(Pet)

    swim_client.register_classes([Person, Pet])

    value_downlink = swim_client.downlink_value()
    value_downlink.set_host_uri('ws://localhost:9001')
    value_downlink.set_node_uri('/unit/foo')
    value_downlink.set_lane_uri('person')
    value_downlink.did_set(my_custom_callback_correct)
    value_downlink.open()

    time.sleep(2)

    # TODO this should be deserialized automatically
    person = RecordMap.create()

    pet = RecordMap.create()
    pet.add(Attr.create_attr(Text.create_from('Pet'), Extant.get_extant()))
    pet.add(Slot.create_slot(Text.create_from('age'), Num.create_from(2)))
    pet.add(Slot.create_slot(Text.create_from('name'), Text.create_from('Bark')))

    person.add(Attr.create_attr(Text.create_from('Person'), Extant.get_extant()))
    person.add(Slot.create_slot(Text.create_from('name'), Text.create_from('Bar')))
    person.add(Slot.create_slot(Text.create_from('age'), Num.create_from(14)))
    person.add(Slot.create_slot(Text.create_from('salary'), Num.create_from(-5.9)))
    person.add(Slot.create_slot(Text.create_from('pet'), pet))

    # new_value = Text.create_from('Foo')
    # new_value = body

    value_downlink.set(person)
    time.sleep(2)
    print('Stopping the client in 2 seconds')
    time.sleep(2)
