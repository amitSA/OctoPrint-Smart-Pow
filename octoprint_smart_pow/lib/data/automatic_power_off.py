from enum import Enum, auto
from dataclasses import dataclass

AUTOMATIC_POWER_OFF_API_COMMAND = "enable_automatic_power_off"
AUTOMATIC_POWER_OFF_SCHEDULED_API_KEY = (
    "automatic_power_off_enabled"  # boolean valued data type
)


@dataclass
class ScheduledPowerOffState:
    scheduled: bool
