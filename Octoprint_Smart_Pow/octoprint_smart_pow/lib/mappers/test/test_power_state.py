
import pytest
from octoprint_smart_pow.lib.data.power_state_api import APIPowerState
from octoprint_smart_pow.lib.data.power_state_changed_event import PowerState
from octoprint_smart_pow.lib.mappers.power_state import (UnsupportedState, power_state_to_api_repr, api_power_state_to_internal_repr)


def test_power_state_to_api_repr():
    assert power_state_to_api_repr(PowerState.OFF) == APIPowerState.OFF
    assert power_state_to_api_repr(PowerState.ON) == APIPowerState.ON
    with pytest.raises(UnsupportedState):
        power_state_to_api_repr("undefined")


def test_api_power_state_to_internal_repr():
    assert api_power_state_to_internal_repr(APIPowerState.OFF) == PowerState.OFF
    assert api_power_state_to_internal_repr(APIPowerState.ON) == PowerState.ON
    with pytest.raises(UnsupportedState):
        api_power_state_to_internal_repr("undefined")
