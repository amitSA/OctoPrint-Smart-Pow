from dataclasses import dataclass
from enum import Enum
from typing import NewType

# Events
class PowerState(Enum):
    ON = "On"
    OFF = "Off"
    UNKNOWN = "Unknown"


# API
POWER_STATE_DO_CHANGE_API_COMMAND = "set_power_state"

API_POWER_STATE_KEY = "power_state"
# Type for a dict object representing PowerState data consumable by APIs
# Required Keys:
#   API_POWER_STATE_KEY: bool
# TODO In python3.8 I can use DictType instead and force required keys
APIPowerState = dict
