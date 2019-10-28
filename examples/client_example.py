import time

from swim import SwimClient, Text


async def my_custom_did_set_async(new_value, old_value):
    print(f'link watched info change to {new_value} from {old_value}')


if __name__ == '__main__':
    # swim_client = SwimClient()
    with SwimClient() as swim_client:
        host_uri = 'ws://localhost:9001'
        # host_uri2 = 'ws://localhost:9002'
        node_uri = '/unit/foo'
        lane_uri = 'info'

        # swim_client.command(host_uri2, node_uri, 'publish', Num.create_from(13))
        link = swim_client.downlink_value().set_host_uri(host_uri).set_node_uri(node_uri).set_lane_uri(lane_uri).did_set(
            my_custom_did_set_async).open()
        link.set(Text.create_from('Test'))

        time.sleep(2)
        link.close()

        time.sleep(2)
        # swim_client.command(host_uri, node_uri, 'publishInfo', Text.create_from('1_2'))
        # swim_client.command(host_uri2, node_uri, 'publish', Num.create_from(37))
        # swim_client.command(host_uri, node_uri, 'publishInfo', Text.create_from('1_3'))
        print("Will shut down client in 2 seconds")
        time.sleep(2)

    time.sleep(2)
