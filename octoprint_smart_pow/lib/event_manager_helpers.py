from octoprint_smart_pow.lib.data.automatic_power_off import (
    ScheduledPowerOffState,
)
from octoprint_smart_pow.lib.data.events import Events
from octoprint_smart_pow.lib.data.power_state import PowerState
from octoprint_smart_pow.lib.mappers.automatic_power_off import (
    scheduled_power_off_state_to_api_repr,
)
from octoprint_smart_pow.lib.mappers.power_state import power_state_to_api_repr


def fire_power_state_changed_event(event_manager, power_state: PowerState):
    event_manager.fire(
        event=Events.POWER_STATE_CHANGED_EVENT(),
        payload=power_state_to_api_repr(power_state),
    )


def fire_power_state_do_change_event(event_manager, power_state: PowerState):
    event_manager.fire(
        event=Events.POWER_STATE_DO_CHANGE_EVENT(),
        payload=power_state_to_api_repr(power_state),
    )


def fire_automatic_power_off_do_change_event(
    event_manager, state: ScheduledPowerOffState
):
    event_manager.fire(
        event=Events.AUTOMATIC_POWER_OFF_DO_CHANGE_EVENT(),
        payload=scheduled_power_off_state_to_api_repr(state),
    )


def fire_automatic_power_off_changed_event(
    event_manager, state: ScheduledPowerOffState
):
    event_manager.fire(
        event=Events.AUTOMATIC_POWER_OFF_CHANGED_EVENT(),
        payload=scheduled_power_off_state_to_api_repr(state),
    )
