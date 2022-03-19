from octoprint_smart_pow.lib.mappers.automatic_power_off import (
    scheduled_power_off_state_to_api_repr,
)
import pytest
import asyncio
import octoprint
from datetime import timedelta
from octoprint_smart_pow.lib.data.automatic_power_off import (
    ScheduledPowerOffState,
)
from octoprint_smart_pow.lib.data.events import Events
from octoprint_smart_pow.lib.data.power_state import PowerState
from octoprint_smart_pow.lib.features.automatic_power_off import (
    AutomaticPowerOff,
)
from octoprint_smart_pow.lib.wait_utils import wait_untill, wait_untill_event
from octoprint_smart_pow.lib.mappers.power_state import power_state_to_api_repr


class TestAutomaticPowerOff:
    @pytest.fixture
    def auto_power_off(self, event_manager):
        auto_power_off = AutomaticPowerOff(
            event_manager, printer_ready_to_shutdown=lambda: True
        )
        yield auto_power_off
        if auto_power_off.enabled:
            auto_power_off.disable()

    @pytest.mark.asyncio
    async def test_will_not_shutdown_if_printer_not_started(
        self, event_manager, auto_power_off
    ):
        auto_power_off.enable()

        event_manager.fire(event=octoprint.events.Events.PRINT_DONE)

        await wait_untill_event(
            event_manager=event_manager,
            event=Events.POWER_STATE_DO_CHANGE_EVENT(),
            payload=power_state_to_api_repr(PowerState.OFF),
            timeout=timedelta(seconds=10),
        ),

    @pytest.mark.asyncio
    async def test_shutdowns_printer_after_print_finished(
        self, event_manager, auto_power_off: AutomaticPowerOff
    ):
        auto_power_off.enable()

        event_manager.fire(event=octoprint.events.Events.PRINT_STARTED)

        event_manager.fire(event=octoprint.events.Events.PRINT_DONE)

        await wait_untill_event(
            event_manager=event_manager,
            event=Events.POWER_STATE_DO_CHANGE_EVENT(),
            payload=power_state_to_api_repr(PowerState.OFF),
            timeout=timedelta(seconds=10),
        ),
        await wait_untill(
            condition=lambda: auto_power_off.get_state().scheduled is False,
            condition_name="Automatic power off should be turned off after activated once",
        )

    @pytest.mark.asyncio
    async def test_cancel_shutdown_if_new_print_starts(
        self, event_manager, auto_power_off
    ):
        auto_power_off.enable()

        event_manager.fire(event=octoprint.events.Events.PRINT_STARTED)

        event_manager.fire(event=octoprint.events.Events.PRINT_DONE)

        # Wait untill the poweroff is scheduled before continuing the test
        #   because the goal of this test is to verify that the schedule can be
        #   disabled after turning on
        await wait_untill_event(
            event_manager=event_manager,
            event=Events.AUTOMATIC_POWER_OFF_CHANGED_EVENT(),
            payload=scheduled_power_off_state_to_api_repr(
                ScheduledPowerOffState(scheduled=True)
            ),
            timeout=timedelta(seconds=10),
        ),

        event_manager.fire(event=octoprint.events.Events.PRINT_STARTED)

        # Verify that the scheduled shutdown is stopped
        # Why? Because after a new print is started we don't want to shutdown!
        await wait_untill_event(
            event_manager=event_manager,
            event=Events.AUTOMATIC_POWER_OFF_CHANGED_EVENT(),
            payload=scheduled_power_off_state_to_api_repr(
                ScheduledPowerOffState(scheduled=False)
            ),
            timeout=timedelta(seconds=10),
        ),

    @pytest.mark.asyncio
    async def test_nothing_happens_if_feature_is_not_enabled(
        self, event_manager, auto_power_off
    ):
        # Don't enable!
        # auto_power_off.enable()

        assert auto_power_off.enabled is False

        # The timer should not be turned on to trigger auto_power_off
        with pytest.raises(TimeoutError):
            await wait_untill_event(
                event_manager=event_manager,
                event=AutomaticPowerOff.TIMEOUT_EVENT,
                timeout=timedelta(seconds=10),
            ),
