import time
from datetime import datetime,timedelta
from octoprint_smart_pow.lib.clock_utils import wait_untill
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


def test_wait_untill_passes(mocked_time, mocked_condition):
    wait_untill(condition=mocked_condition,
                poll_period=timedelta(seconds=1),
                timeout=timedelta(seconds=4),
                time=mocked_time,
                sleep=lambda x:True)

    assert len(mocked_condition.call_args_list) == 4

def test_wait_untill_fails(mocked_time, mocked_condition):
    with pytest.raises(TimeoutError):
        wait_untill(condition=mocked_condition,
                    poll_period=timedelta(seconds=1),
                    timeout=timedelta(seconds=3),
                    time=mocked_time,
                    sleep=lambda x:True)
