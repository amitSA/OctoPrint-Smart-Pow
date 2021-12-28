from enum import Enum
API_POWER_STATE_KEY = "power_state"
API_POWER_STATE_SET_COMMAND = "set_power_state"
class APIPowerState(Enum):
    ON = "on"
    OFF = "off"
