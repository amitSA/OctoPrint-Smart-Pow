import time
from datetime import datetime, timedelta
import funcy


def wait_untill(
    condition,
    poll_period=timedelta(seconds=1),
    timeout=timedelta(seconds=10),
    condition_name="no_name",
    time=time.time,
    sleep=time.sleep,
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
        sleep(poll_period.total_seconds())
        condition_is_true = cond_callable()

    if not condition_is_true:
        raise TimeoutError(
            f"Waited {timeout} time for condition '{condition_name}' to be True"
        )
