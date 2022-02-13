# XXX Rename this to "interval_scheduler.py" and delete the old file after this is confirmed to work for both async and regula routines
# XXX Rename this class to represent running the same routine to run in an interval
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

    def __init__(self, routine: Callable, interval: timedelta, logger=logging):
        self.routine = routine
        self.interval_seconds = interval.total_seconds()

        self.t_helper = threading.Thread(target=self.__run)
        self.should_exit = False
        self.logger = logger
        self._has_finished = False

    def __run(self):
        """
        The core logic of the scheduler that also calls the scheduler's routine.
        """
        asyncio.run(self.__loop())

    async def __loop(self):
        while not self.should_exit:
            result = self.routine()
            if asyncio.iscoroutine(result):
                await result

            await asyncio.sleep(self.interval_seconds)
        self._has_finished = True
        self.logger.info("Scheduler exited succesfully!")

    def start(self):
        self.t_helper.start()

    def stop(self):
        self.should_exit = True

    def has_finished(self):
        return self._has_finished

    def running(self):
        """
        Returns whether start() has been called before a stop()
        """
        return self.t_helper.is_alive()


# I used this as a manual test since it was quicker than writing unit-tests. HarHarHar
if __name__ == "__main__":
    squak = lambda: print("Caaw!")
    scheduler = AsyncIntervalScheduler(
        routine=squak, interval=timedelta(seconds=1)
    )
    scheduler.start()
