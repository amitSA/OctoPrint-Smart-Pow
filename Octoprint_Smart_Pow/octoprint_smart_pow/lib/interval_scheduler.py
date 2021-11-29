
from datetime import timedelta
from typing import Callable
import sched
import threading
import time
import logging

class IntervalScheduler:
    """
    Runs a routine at an interval out of the calling thread
    """
    HIGH_PRIORITY = 0
    def __init__(self,action: Callable, interval: timedelta, get_time=time.time,wait=time.sleep):
        self.action = action
        self.interval_seconds = interval.total_seconds()
        self.scheduler = sched.scheduler(get_time,wait)

        self.t_helper = threading.Thread(target=self.__run)
        self.should_exit = False

    def __run(self):
        """
        The core logic of the scheduler that also calls the scheduler's action.

        This is a blocking call, and thus should be called within a dedicated thread.
        """
        def action_wrapper():
            self.action()
            self.__run()

        if self.should_exit:
            return

        self.scheduler.enter(delay=self.interval_seconds,priority=self.HIGH_PRIORITY,action=action_wrapper)
        # Runs all scheduled events, and blocks untill completion
        self.scheduler.run()

    def start(self):
        self.t_helper.start()

    def stop(self):
        self.should_exit = True


if __name__ == "__main__":
    squak = lambda: print("Caaw!")
    scheduler = IntervalScheduler(action=squak,interval=timedelta(seconds=1))
    scheduler.start()