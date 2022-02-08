import time
from datetime import datetime, timedelta
import funcy
from unittest import mock
import asyncio
from octoprint.events import EventManager


async def wait_untill(
    condition,
    poll_period=timedelta(seconds=1),
    timeout=timedelta(seconds=10),
    condition_name="no_name",
    time=time.time,
    *condition_args,
    **condition_kwargs,
):
    """
    Waits untill the following condition function returns true

    args:
        condition: A zero-arity callable
        poll_period: How often to call the condition
        time: Callable that returns the current time in seconds since epoch
        sleep: Callable that blocks the thread for a certain amount of seconds
        timeout: Total time to wait for the condition
        condition_name: A human friendly name for the condition that will be mentioned in the Timeout error

    throws:
        TimeoutError
    """
    # holds the starting time in seconds since the epoch
    start_time = int(time())
    cond_callable = funcy.partial(condition, *condition_args, **condition_kwargs)
    condition_is_true = cond_callable()
    while (
        int(time()) < start_time + timeout.total_seconds()
        and not condition_is_true
    ):
        await asyncio.sleep(poll_period.total_seconds())
        condition_is_true = cond_callable()

    if not condition_is_true:
        raise TimeoutError(
            f"Waited {timeout} time for condition '{condition_name}' to be True"
        )


async def wait_untill_event(
    event_manager: EventManager,
    event,
    payload=None,
    poll_period=timedelta(seconds=1),
    timeout=timedelta(seconds=10),
):
    try:
        subscriber = mock.Mock()

        def event_was_published():
            return subscriber.call_args == mock.call(event, payload)

        event_manager.subscribe(event=event, callback=subscriber)
        await wait_untill(
            condition=event_was_published,
            poll_period=poll_period,
            timeout=timeout,
            condition_name=f"Event {event} was published",
        )
    finally:
        event_manager.unsubscribe(event=event, callback=subscriber)
