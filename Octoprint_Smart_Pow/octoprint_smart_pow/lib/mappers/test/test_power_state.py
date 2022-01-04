
import pytest
from octoprint_smart_pow.lib.data.power_state import API_POWER_STATE_KEY, APIPowerState, PowerState
from octoprint_smart_pow.lib.mappers.power_state import (power_state_to_api_repr, api_power_state_to_internal_repr)

@pytest.fixture
def api_power_state_off():
    return {
            API_POWER_STATE_KEY: "Off"
    }

@pytest.fixture
def api_power_state_on():
    return {
            API_POWER_STATE_KEY: "On"
    }

def test_power_state_to_api_repr(api_power_state_off,api_power_state_on):
    assert power_state_to_api_repr(PowerState.OFF) == api_power_state_off
    assert power_state_to_api_repr(PowerState.ON) == api_power_state_on



def test_api_power_state_to_internal_repr(api_power_state_off,api_power_state_on):
    assert api_power_state_to_internal_repr(
        api_power_state_off
    ) == PowerState.OFF
    assert api_power_state_to_internal_repr(
        api_power_state_on
    ) == PowerState.ON
