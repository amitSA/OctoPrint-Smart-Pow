import asyncio
import time
from datetime import datetime, timedelta
from octoprint_smart_pow.lib.wait_utils import wait_untill, wait_untill_event
import logging
import pytest
import funcy


@pytest.fixture
def mocked_time(mocker):
    mocked_time = mocker.Mock()
    # each call to mocked_time will return the next value in the list
    mocked_time.side_effect = range(10)
    return mocked_time


@pytest.fixture
def mocked_condition(mocker):
    mocked_condition = mocker.Mock()
    mocked_condition.side_effect = [False, False, False, True]
    return mocked_condition


@pytest.mark.asyncio
async def test_wait_untill_passes(mocked_time, mocked_condition):
    await wait_untill(
        condition=mocked_condition,
        poll_period=timedelta(seconds=1),
        timeout=timedelta(seconds=4),
        time=mocked_time,
        sleep=lambda x: True,
    )

    assert len(mocked_condition.call_args_list) == 4


@pytest.mark.asyncio
async def test_wait_untill_fails(mocked_time, mocked_condition):
    with pytest.raises(TimeoutError):
        await wait_untill(
            condition=mocked_condition,
            poll_period=timedelta(seconds=1),
            timeout=timedelta(seconds=3),
            time=mocked_time,
            sleep=lambda x: True,
        )


@pytest.fixture
def publish(event_manager):
    """
    Returns a function that will publish an event
    """

    async def _publish(event, payload=None):
        event_manager.fire(event, payload)

    return _publish


@pytest.mark.asyncio
async def test_wait_untill_event_passes(event_manager, publish):
    await asyncio.gather(
        wait_untill_event(event_manager=event_manager, event="TEST_EVENT"),
        publish(event="TEST_EVENT"),
    )

    await asyncio.gather(
        wait_untill_event(
            event_manager=event_manager, event="TEST_EVENT", payload="hi"
        ),
        publish(event="TEST_EVENT", payload="hi"),
    )


@pytest.mark.asyncio
async def test_wait_untill_event_fails(event_manager, publish):
    """
    Test that wait_untill_event fails when it's supposed to,
    which is when no event with the same name and payload is received

    So we assert that it fails when two events are fired, one
    with a mismatched payload, and the other with a mismatched event
    """
    with pytest.raises(TimeoutError):
        await asyncio.gather(
            wait_untill_event(
                event_manager=event_manager, event="TEST_EVENT", payload="a"
            ),
            # event with mismatched payload
            publish(event="TEST_EVENT", payload="b"),
            # event with mismatched event string
            publish(event="TEST_EVEN", payload="a"),
        )
