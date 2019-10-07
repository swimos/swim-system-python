import time

from swimai.client.swim_client import SwimClient

if __name__ == '__main__':
    swim_client = SwimClient()
    swim_client.start()

    swim_client.schedule_task(1)
    swim_client.schedule_task(2)
    time.sleep(5)

    print("Main")
    # swim_client.unschedule_task()
    time.sleep(5)
    swim_client.stop()

    # host_uri = 'warp://localhost:9001'
    # node_Uri = '/unit/foo'

    # swim_client.stop()
    # time.sleep(5)
    # print("Main 2")
    # time.sleep(5)
    # print("Main 3")
    # link = swim_client.downlink_value().set_host_uri(host_uri).set_node_uri(node_Uri).set_lane_uri('info').did_set(
    #     lambda new_value, old_value: print(f'link watched info change to {new_value} from {old_value}')).open()
    #
    # # link.set(Text.from_string('Hello from link, world!'))
    #
    # print("synchronous link get: " + link.get())
    #
    # print("Will shut down client in 2 seconds")
    # time.sleep(2000)
    # swim_client.stop()
