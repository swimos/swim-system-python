import asyncio
import time

from swimai.client.swim_client import SwimClient
from swimai.structure.structs import Text


async def my_custom_did_set_async(new_value, old_value):
    print(f'link watched info change to {new_value} from {old_value}')
    await asyncio.sleep(15)
    # print("Wake up!")


def my_custom_did_set_sync(new_value, old_value):
    print(f'link watched info change to {new_value} from {old_value}')
    # time.sleep(15)
    # print("Wake up!")


if __name__ == '__main__':
    swim_client = SwimClient()
    swim_client.start()

    host_uri = 'ws://localhost:9001'
    node_uri = '/unit/foo'
    lane_uri = 'info'

    link = swim_client.downlink_value().set_host_uri(host_uri).set_node_uri(node_uri).set_lane_uri(lane_uri).did_set(my_custom_did_set_async).open()

    link.set(Text.get_from('Hello from Python'))

    # print("synchronous link get: " + link.get())

    # Optional
    # link.close()
    time.sleep(2)
    print("Will shut down client in 2 seconds")
    time.sleep(2)
    swim_client.stop()
