import asyncio
import time

from swimai.client.swim_client import SwimClient


async def my_custom_did_set(new_value, old_value):
    print(f'link watched info change to {new_value} from {old_value}')
    await asyncio.sleep(5)
    print("Wake up!")

if __name__ == '__main__':
    swim_client = SwimClient()
    swim_client.start()

    host_uri = 'warp://localhost:9001'
    node_Uri = '/unit/foo'
    lane_uri = 'info'

    link = swim_client.downlink_value().set_host_uri(host_uri).set_node_uri(node_Uri).set_lane_uri(lane_uri).did_set(my_custom_did_set).open()

    # link.set(Text.from_string('Hello from link, world!'))
    # print("synchronous link get: " + link.get())

    # Optional
    # link.close()

    print("Will shut down client in 2 seconds")
    time.sleep(2)
    # swim_client.stop()
