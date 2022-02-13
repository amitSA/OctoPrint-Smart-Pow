import funcy
from octoprint_smart_pow.lib.data.power_state import (
    API_POWER_STATE_KEY,
    APIPowerState,
)
from octoprint_smart_pow.lib.data.power_state import PowerState


def power_state_to_api_repr(state: PowerState) -> APIPowerState:
    return APIPowerState(**{API_POWER_STATE_KEY: state.value})


def api_power_state_to_internal_repr(api_state: APIPowerState) -> PowerState:
    return PowerState(api_state[API_POWER_STATE_KEY])
