from dataclasses import dataclass
from enum import Enum

POWER_STATE_CHANGED_EVENT = "power_state_changed"

class PowerState(Enum):
  ON = 0
  OFF = 1

@dataclass
class PowerStateChangedEventPayload:
    power_state: PowerState