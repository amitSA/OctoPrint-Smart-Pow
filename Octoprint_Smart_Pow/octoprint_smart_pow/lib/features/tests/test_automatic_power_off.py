
import pytest
import asyncio
from datetime import timedelta
from octoprint_smart_pow.lib.data.automatic_power_off import ScheduledPowerOffState
from octoprint_smart_pow.lib.data.events import Events
from octoprint_smart_pow.lib.data.power_state import PowerState
from octoprint_smart_pow.lib.event_manager_helpers import fire_automatic_power_off_do_change_event
from octoprint_smart_pow.lib.features.automatic_power_off import AutomaticPowerOff
from octoprint_smart_pow.lib.wait_utils import wait_untill_event
from octoprint_smart_pow.lib.mappers.power_state import power_state_to_api_repr

class TestAutomaticPowerOff:

    @pytest.fixture
    def auto_power_off(self, event_manager):
        auto_power_off = AutomaticPowerOff(event_manager, printer_ready_to_shutdown=lambda: True)
        yield auto_power_off
        if auto_power_off.enabled:
            auto_power_off.disable()

    @pytest.mark.asyncio
    async def test_shutdown_after_print_finishes(self, event_manager, auto_power_off):
        auto_power_off.enable()

        fire_automatic_power_off_do_change_event(
            event_manager,
            ScheduledPowerOffState(scheduled=True)
        )
        # The order matters of gathered co-routines because
        # the wait will yield execution after it's listening for events
        await asyncio.gather(
            wait_untill_event(
                event_manager=event_manager,
                event=Events.POWER_STATE_DO_CHANGE_EVENT(),
                payload=power_state_to_api_repr(PowerState.OFF),
                timeout=timedelta(seconds=10),
            ),
        )
        auto_power_off.disable()

    def test_will_not_shutdown_if_not_scheduled(self, event_manager):
        pass

    def test_cancel_shutdown_if_new_print_starts(self, event_manager):
        pass
