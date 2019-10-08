class ValueDownlink:

    def __init__(self, client):
        self.client = client
        self.host_uri = None
        self.node_uri = None
        self.lane_uri = None

        self.value = None

    async def execute_did_set(self, new_value, old_value):
        # no-op
        pass

    # async def async_wrapper(self, function, *args):
    #     await function(*args)

    def set_host_uri(self, host_uri):
        self.host_uri = host_uri
        return self

    def set_node_uri(self, node_uri):
        self.node_uri = node_uri
        return self

    def set_lane_uri(self, lane_uri):
        self.lane_uri = lane_uri
        return self

    def did_set(self, function):
        self.execute_did_set = function
        return self

    def open(self):
        self.client.schedule_task(self.__open)

        return self

    async def __open(self):
        await self.client.open_websocket()
        await self.establish_downlink()
        await self.handle_message()

    def create_downlink_message(self):
        # TODO define parser to handle the encoding of messages
        return f'@sync(node:"{self.node_uri}",lane:{self.lane_uri})'

    async def establish_downlink(self):
        await self.client.websocket.send(self.create_downlink_message())

    async def handle_message(self):
        while True:
            response = await self.client.websocket.recv()

            # TODO define parser to handle the decoding of messages

            if 'event' in response:
                data = response.split(')')

                if len(data) > 1:
                    old_value = self.value
                    self.value = data[1]

                    # Schedule a task
                    self.client.schedule_task(self.execute_did_set, self.value, old_value)

                    # self.client.loop.run_in_executor(None, self.execute_did_set, self.value, old_value)
                    # self.execute_did_set(self.value, old_value)

            # if command == 'linked':
            #     did_link()
            # if command == 'synced':
            #     did_sync()
            # if command == 'event':
            #     execute_did_set()

    def get(self):
        pass
