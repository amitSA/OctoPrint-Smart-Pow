
from datetime import timedelta
from octoprint.events import EventManager
from octoprint_smart_pow.lib.smart_plug_client import SmartPlugClient
from octoprint_smart_pow.lib.data.power_state_changed_event import (
    PowerStateChangedEventPayload,
    PowerState
)

from octoprint_smart_pow.lib.interval_scheduler import IntervalScheduler

class PowerStatePublisher:
    """
    Listen to state change events for a a smart power plug, and broadcast them on the EventManager
    """
    def __init__(self, event: str, event_manager : EventManager, smart_plug: SmartPlugClient):
        self.event = event
        self.event_manager = event_manager
        self.smart_plug = smart_plug

        # An object that will call a routine on an interval
        self.interval_scheduler = IntervalScheduler(
            action=self.publish_if_changed,
            interval=timedelta(seconds=5)
        )
        self.last_updated_state = None

    def start(self):
        """
        Start publishing events.
        """
        self.interval_scheduler.start()

    def stop(self):
        """
        Stop publishing events, and cleanup any resources like threads.
        """
        self.interval_scheduler.stop()

    def publish_if_changed(self):
        """
        Publishes a "power state changed" event if it has changed since the last time
        this method was called
        """
        current_state = self.smart_plug.read()
        if self.last_updated_state != current_state:
            self.event_manager.fire(
                event=self.event,
                payload=self.__create_payload(current_state)
            )

    def __create_payload(self, state: PowerState):
        return PowerStateChangedEventPayload(power_state=state)