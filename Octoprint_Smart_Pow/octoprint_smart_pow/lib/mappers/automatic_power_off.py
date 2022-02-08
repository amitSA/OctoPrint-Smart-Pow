from octoprint_smart_pow.lib.data.automatic_power_off import (
    AUTOMATIC_POWER_OFF_SCHEDULED_API_KEY,
    ScheduledPowerOffState,
)


def scheduled_power_off_state_to_api_repr(state: ScheduledPowerOffState):
    return {AUTOMATIC_POWER_OFF_SCHEDULED_API_KEY: state.scheduled}


def api_scheduled_power_off_state_to_internal_repr(
    api_state,
) -> ScheduledPowerOffState:
    return ScheduledPowerOffState(
        scheduled=api_state[AUTOMATIC_POWER_OFF_SCHEDULED_API_KEY]
    )
