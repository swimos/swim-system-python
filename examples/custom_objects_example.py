#  Copyright 2015-2019 SWIM.AI inc.
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

# Setting the value of a value lane on a remote agent.
import time

from examples.person import Person, Pet
from swimai import SwimClient


async def my_custom_callback_correct(new_value, old_value):
    print(f'New: {new_value}')
    print(f'Old: {old_value}')


def my_custom_exception_callback():
    print('custom exception callback')


with SwimClient(debug=True) as swim_client:
    host_uri = 'ws://localhost:9001'
    node_uri = '/unit/foo'

    value_downlink = swim_client.downlink_value()
    # value_downlink.register_class(Person)
    # value_downlink.register_class(Pet)
    value_downlink.set_host_uri('ws://localhost:9001')
    value_downlink.set_node_uri('/unit/foo')
    value_downlink.set_lane_uri('person')
    value_downlink.did_set(my_custom_callback_correct)
    value_downlink.open()

    time.sleep(2)

    person = Person(name='Bar', age=14, salary=-5.9, pet=Pet(age=2, name='Bark'))
    value_downlink.set(person)
    time.sleep(2)
    print('Stopping the client in 2 seconds')
    time.sleep(2)
