import asyncio
from threading import Thread

from swimai.client.downlinks.value_downlink import ValueDownlink


class SwimClient:

    def __init__(self):
        self.downlinks = list()
        self.loop = None

    def downlink_value(self):
        return ValueDownlink(self)

    def start(self):
        thread = Thread(target=self.event_loop)
        thread.start()

    def stop(self):
        for task in asyncio.all_tasks(self.loop):
            task.cancel()

        while len(asyncio.all_tasks(self.loop)) > 0:
            pass

        self.loop.stop()

    def event_loop(self):
        loop = asyncio.new_event_loop()
        self.loop = loop
        asyncio.set_event_loop(loop)
        asyncio.get_event_loop().run_forever()

    async def example_function(self, seconds):
        while True:
            await asyncio.sleep(seconds)
            print(seconds)

    def schedule_task(self, time):
        asyncio.run_coroutine_threadsafe(self.example_function(time), loop=self.loop)

    def unschedule_task(self, task):
        task.cancel()
