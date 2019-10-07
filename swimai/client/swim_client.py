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
        loop = asyncio.new_event_loop()
        self.loop = loop

        thread = Thread(target=self.event_loop)
        thread.start()

    def stop(self):
        self.schedule_any_task(self.__stop_client)

    async def __stop_client(self):
        tasks = [task for task in asyncio.all_tasks(self.loop) if task is not asyncio.current_task(self.loop)]
        [task.cancel() for task in tasks]
        await asyncio.gather(*tasks, return_exceptions=True)

        self.loop.stop()

    def event_loop(self):
        asyncio.set_event_loop(self.loop)
        asyncio.get_event_loop().run_forever()

    async def example_function(self, seconds):
        while True:
            await asyncio.sleep(seconds)
            print(seconds)

    def schedule_any_task(self, task):
        asyncio.run_coroutine_threadsafe(task(), loop=self.loop)

    def schedule_task(self, time):
        asyncio.run_coroutine_threadsafe(self.example_function(time), loop=self.loop)

    def unschedule_task(self, task):
        task.cancel()
