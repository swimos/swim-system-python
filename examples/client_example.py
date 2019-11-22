# Setting the value of a value lane on a remote agent.
import time

from swimai import SwimClient
from swimai.structures import Text

with SwimClient() as swim_client:
    host_uri = 'ws://localhost:9001'
    node_uri = '/unit/foo'
    lane_uri = 'info'

    value_downlink = swim_client.downlink_value()
    value_downlink.set_host_uri('ws://localhost:9001')
    value_downlink.set_node_uri('/unit/foo')
    value_downlink.set_lane_uri('info')
    value_downlink.open()

    new_value = Text.create_from('Hello from Python!')

    value_downlink.set(new_value)
    print('Stopping the client in 2 seconds')
    time.sleep(2)
