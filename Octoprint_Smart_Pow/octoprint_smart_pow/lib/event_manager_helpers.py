from octoprint_smart_pow.lib.data.events import Events
from octoprint_smart_pow.lib.data.power_state import PowerState
from octoprint_smart_pow.lib.mappers.power_state import power_state_to_api_repr


def fire_power_state_changed_event(event_manager, power_state: PowerState):
    event_manager.fire(
        event=Events.POWER_STATE_CHANGED_EVENT(),
        payload=power_state_to_api_repr(power_state),
    )
