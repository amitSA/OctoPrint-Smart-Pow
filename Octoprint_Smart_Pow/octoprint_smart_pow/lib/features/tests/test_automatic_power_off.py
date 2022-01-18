

from datetime import timedelta
from octoprint_smart_pow.lib.data.automatic_power_off import ScheduledPowerOffState
from octoprint_smart_pow.lib.data.power_state import PowerState
from octoprint_smart_pow.lib.event_manager_helpers import fire_automatic_power_off_do_change_event
from octoprint_smart_pow.lib.features.automatic_power_off import AutomaticPowerOff


class TestAutomaticPowerOff:


    def test_shutdown_after_print_finishes(self, event_manager):
        auto_power_off = AutomaticPowerOff(event_manager, printer=None)

        # I wonder if we can encapsulate this logic separately with it's single control
        turn_off_flag = False
        def mocked_turn_off_condition():
            return turn_off_flag
        mocker.Mock.patch("_AutomaticPowerOff__mocked_turn_off_condition",mocked_turn_off_condition)

        auto_power_off.enable()
        fire_automatic_power_off_do_change_event(
            event_manager,
            ScheduledPowerOffState(scheduled=True)
        )
        turn_off_flag = True
        wait_untill_event(
            event_manager=event_manager,
            event=events.POWER_STATE_CHANGED_EVENT(),
            payload=power_state_to_api_repr(PowerState.OFF),
            timeout=timedelta(seconds=10),
        )
        # Condition name can be extrapolated from this derivitive of wait_untill


    def test_will_not_shutdown_if_not_scheduled(self, event_manager):
        pass

    def test_cancel_shutdown_if_new_print_starts(self, event_manager):
        auto_power_off = AutomaticPowerOff(event_manager, printer=None)
