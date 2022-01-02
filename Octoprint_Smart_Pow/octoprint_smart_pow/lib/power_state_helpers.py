from octoprint_smart_pow.lib.data.power_state_changed_event import POWER_STATE_CHANGED_EVENT, PowerState
from octoprint_smart_pow.lib.mappers.power_state import power_state_to_event_payload


def fire_power_state_changed_event(event_manager, power_state: PowerState):
    event_manager.fire(
        event=POWER_STATE_CHANGED_EVENT,
        payload=power_state_to_event_payload(power_state),
    )
