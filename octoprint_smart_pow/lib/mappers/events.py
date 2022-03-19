from octoprint_smart_pow.lib.data.events import Events
from octoprint_smart_pow.lib.data.power_state import PowerState
from octoprint_smart_pow.lib.mappers.automatic_power_off import api_scheduled_power_off_state_to_internal_repr, scheduled_power_off_state_to_api_repr
from octoprint_smart_pow.lib.mappers.power_state import api_power_state_to_internal_repr, power_state_to_api_repr
from octoprint.events import EventManager

def fire_event(event_manager: EventManager, event, app_data=None, serialized_data=None):
    serializer = {
        Events.POWER_STATE_CHANGED_EVENT(): power_state_to_api_repr,
        Events.POWER_STATE_DO_CHANGE_EVENT(): power_state_to_api_repr,
        Events.AUTOMATIC_POWER_OFF_DO_CHANGE_EVENT(): scheduled_power_off_state_to_api_repr,
        Events.AUTOMATIC_POWER_OFF_CHANGED_EVENT(): scheduled_power_off_state_to_api_repr
    }[event]
    if serialized_data is None:
        event_manager.fire(event,payload=serializer(app_data))
    else:
        event_manager.fire(event,payload=serialized_data)


def parse_event_payload(source_event, serialized_data):
    deserializer = {
        Events.POWER_STATE_CHANGED_EVENT(): api_power_state_to_internal_repr,
        Events.POWER_STATE_DO_CHANGE_EVENT(): api_power_state_to_internal_repr,
        Events.AUTOMATIC_POWER_OFF_DO_CHANGE_EVENT():  api_scheduled_power_off_state_to_internal_repr,
        Events.AUTOMATIC_POWER_OFF_CHANGED_EVENT(): api_scheduled_power_off_state_to_internal_repr,
    }[source_event]
    return deserializer(serialized_data)
