import pytest
from datetime import timedelta

from octoprint_smart_pow.lib.async_interval_scheduler import (
    AsyncIntervalScheduler,
)
from octoprint_smart_pow.lib.wait_utils import wait_untill


class TestAsyncIntervalScheduler:
    @pytest.mark.asyncio
    async def test_running_routine(self, mocker):
        EXPECTED_ROUTINE_CALLS = 3

        closure = {"calls": 1}

        def routine():
            # We can control how many times this is supposed to be called by the
            # AsyncIntervalScheduler by passing the scheduler via closure,
            # and stopping scheduling after the desired number of calls
            if closure["calls"] == EXPECTED_ROUTINE_CALLS:
                # Based from how the scheduler works, after calling stop()
                # there should be no more calls to routine
                closure["scheduler"].stop()
            closure["calls"] += 1

        # TODO: Once migrated to python3.8, we can also test async routines with mocker.AsyncMock
        mocked_routine = mocker.Mock(wraps=routine)

        scheduler = AsyncIntervalScheduler(
            routine=mocked_routine, interval=timedelta(seconds=0)
        )
        closure["scheduler"] = scheduler

        scheduler.start()
        await wait_untill(
            condition=lambda: scheduler.has_finished(),
            condition_name="scheduler has finished",
        )
        assert len(mocked_routine.call_args_list) == EXPECTED_ROUTINE_CALLS
