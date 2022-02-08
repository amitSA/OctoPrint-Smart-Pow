import funcy
from datetime import timedelta
from typing import Callable
import octoprint.printer
import octoprint.events
from octoprint.events import EventManager
from octoprint_smart_pow.lib.async_interval_scheduler import (
    AsyncIntervalScheduler,
)
from octoprint_smart_pow.lib.data.automatic_power_off import (
    ScheduledPowerOffState,
)
from octoprint_smart_pow.lib.data.events import Events
from octoprint_smart_pow.lib.data.power_state import PowerState
from octoprint_smart_pow.lib.event_manager_helpers import (
    fire_automatic_power_off_do_change_event,
    fire_automatic_power_off_changed_event,
    fire_power_state_do_change_event,
)
from octoprint_smart_pow.lib.mappers.automatic_power_off import (
    api_scheduled_power_off_state_to_internal_repr,
)


class AutomaticPowerOff:

    # This is the event passed to event manager
    # It's defined outside of lib/data/events.py because it is specific to this
    # class.
    # TODO consider moving this timer outside of this class in order to support 1:N relationship
    # of timer to client classes.
    #   A good candidate might be adding a class methods in eevnts.py to create timers
    #   and have __init__.py pass the timer event as a constructor to this class.
    TIMEOUT_EVENT = "plugin_smart_pow_timeout"

    def __init__(
        self,
        event_manager: EventManager,
        printer_ready_to_shutdown: Callable[[], bool],
    ):
        self.state = ScheduledPowerOffState(scheduled=False)
        self.printer_ready_to_shutdown = printer_ready_to_shutdown
        self.event_manager = event_manager
        self.timer = None

    def get_state(self) -> ScheduledPowerOffState:
        return self.state

    def __get_print_finished_events(self):
        """
        All events regarding the finishing of a print
        """
        return [
            octoprint.events.Events.PRINT_DONE,
        ]

    def __get_events(self):
        """
        Return all the event's that should be subscribed to
        """
        return [
            self.TIMEOUT_EVENT,
            octoprint.events.Events.PRINT_STARTED,
            octoprint.events.Events.PRINT_DONE,
            Events.AUTOMATIC_POWER_OFF_DO_CHANGE_EVENT(),
        ]

    def __init_timer(self):
        """
        Initializes a new timer.

        @precondition: The current timer should be either not initialized
        or have exited in the past, since this doesn't stop running timers
        """

        def post_timeout_events():
            self.event_manager.fire(
                event=self.TIMEOUT_EVENT,
            )

        if self.timer is None or self.timer.has_finished():
            self.timer = AsyncIntervalScheduler(
                post_timeout_events, timedelta(seconds=5)
            )
        else:
            raise ValueError(
                "Timer object first needs to be stopped before it's garbage collected"
            )

    def enable(self):
        """
        Enable this feature.

        This is needed in order to schedule power offs
        """
        self.__init_timer()
        self.timer.start()
        self.__subscribe(events=self.__get_events(), callback=self.on_event)

    def disable(self):
        """
        Disable this feature.

        A scheduled power-off will automatically be unscheduled
        """
        if not self.enabled:
            raise RuntimeError("Cannot disabled if it hasn't been enabled yet")

        # TODO is self.on_event the same as before ?
        self.__unsubscribe(events=self.__get_events(), callback=self.on_event)
        self.timer.stop()

    @property
    def enabled(self):
        return self.timer is not None and self.timer.running()

    def on_event(self, event: octoprint.events.Events, payload):
        """
        A Finite State Machine (FSM) to implement behavior of smartly turning off
        power
        """
        if event == self.TIMEOUT_EVENT:
            if self.state.scheduled and self.printer_ready_to_shutdown():
                fire_power_state_do_change_event(
                    self.event_manager, power_state=PowerState.OFF
                )
                # After shuttdown power, disable the scheduling automation
                #   or else the system will fight the user the next time they
                #   turn it on!
                fire_automatic_power_off_do_change_event(
                    self.event_manager, ScheduledPowerOffState(scheduled=False)
                )
        elif event == octoprint.events.Events.PRINT_STARTED:
            fire_automatic_power_off_do_change_event(
                self.event_manager, ScheduledPowerOffState(scheduled=False)
            )
        elif event in [octoprint.events.Events.PRINT_DONE]:
            fire_automatic_power_off_do_change_event(
                self.event_manager, ScheduledPowerOffState(scheduled=True)
            )
        elif event == Events.AUTOMATIC_POWER_OFF_DO_CHANGE_EVENT():
            desired_state = api_scheduled_power_off_state_to_internal_repr(
                payload
            )
            if self.state.scheduled != desired_state.scheduled:
                self.state = desired_state
                fire_automatic_power_off_changed_event(
                    self.event_manager, self.state
                )

    def __subscribe(self, events, callback):
        for event in events:
            self.event_manager.subscribe(event, callback)

    def __unsubscribe(self, events, callback):
        for event in events:
            self.event_manager.unsubscribe(event, callback)
