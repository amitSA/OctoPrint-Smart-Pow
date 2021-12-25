
# XXX Rename this to "interval_scheduler.py" and delete the old file after this is confirmed to work for both async and regula actions
from datetime import timedelta
from types import coroutine
from typing import Callable, Coroutine
import sched
import threading
import time
import logging
import asyncio

class AsyncIntervalScheduler:
    """
    Runs a routine at an interval out of the calling thread
    """
    HIGH_PRIORITY = 0
    def __init__(self, action: Callable, interval: timedelta, logger=logging):
        self.action = action
        self.interval_seconds = interval.total_seconds()

        self.t_helper = threading.Thread(target=self.__run)
        self.should_exit = False
        self.logger = logger

    def __run(self):
        """
        The core logic of the scheduler that also calls the scheduler's action.
        """
        asyncio.run(self.__loop())

    async def __loop(self):
        while not self.should_exit:
            result = self.action()
            if asyncio.iscoroutine(result):
                await result

            await asyncio.sleep(self.interval_seconds)
        self.logger.info("Scheduler exited succesfully!")

    def start(self):
        self.t_helper.start()

    def stop(self):
        self.should_exit = True


# I used this as a manual test since it was quicker than writing unit-tests. HarHarHar
if __name__ == "__main__":
    squak = lambda: print("Caaw!")
    scheduler = AsyncIntervalScheduler(action=squak,interval=timedelta(seconds=1))
    scheduler.start()
