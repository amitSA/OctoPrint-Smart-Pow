
import funcy
from octoprint_smart_pow.lib.data.power_state_api import APIPowerState
from octoprint_smart_pow.lib.data.power_state_changed_event import PowerState, PowerStateChangedEventPayload

class UnsupportedState(Exception):
    pass


api_to_internal_mapping = {
    PowerState.OFF: APIPowerState.OFF,
    PowerState.ON: APIPowerState.ON,
    PowerState.UNKNOWN: APIPowerState.UNKNOWN,
}
# TODO: I question the use of the data type APIPowerState.  Maybe I should just use "PowerState" as the data contract for the API
# and that would simplify a lot of code
#  One potential pro for doing this is that does it obviate the need to do this mapping in frontend ?
# I ideally want to avoid business logic in frontend as much as possible
def power_state_to_api_repr(state: PowerState) -> APIPowerState:
    try:
        return api_to_internal_mapping[state]
    except KeyError as e:
        raise UnsupportedState(f"power state {state} not recognized") from e

def api_power_state_to_internal_repr(api_state: APIPowerState) -> PowerState:
    internal_to_api_mapping = funcy.flip(api_to_internal_mapping)
    try:
        return internal_to_api_mapping[api_state]
    except KeyError as e:
        raise UnsupportedState(f"api power state {api_state} not recognized") from e

def power_state_to_event_payload(state: PowerState):
    return PowerStateChangedEventPayload(power_state=state)
