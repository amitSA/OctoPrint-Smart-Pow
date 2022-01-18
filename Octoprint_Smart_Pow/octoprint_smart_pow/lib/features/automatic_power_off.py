
from datetime import timedelta
from typing import Callable
import octoprint.printer
import octoprint.events
from octoprint.events import EventManager
from octoprint_smart_pow.lib.async_interval_scheduler import AsyncIntervalScheduler
from octoprint_smart_pow.lib.data.automatic_power_off import ScheduledPowerOffState
from octoprint_smart_pow.lib.data.events import Events
from octoprint_smart_pow.lib.data.power_state import PowerState
from octoprint_smart_pow.lib.event_manager_helpers import fire_automatic_power_off_do_change_event, fire_automatic_power_off_changed_event, fire_power_state_do_change_event
from octoprint_smart_pow.lib.mappers.automatic_power_off import api_scheduled_power_off_state_to_internal_repr

class AutomaticPowerOff:

    # This is the event passed to event manager
    # It's defined outside of lib/data/events.py because it is specific to this
    # class.
    # TODO consider moving this timer outside of this class in order to support 1:N relationship
    # of timer to client classes.
    #   A good candidate might be adding a class methods in eevnts.py to create timers
    #   and have __init__.py pass the timer event as a constructor to this class.
    TIMEOUT_EVENT = "plugin_smart_pow_timeout"

    def __init__(self, event_manager: EventManager, printer, temperature_threshold = 40):
        self.state = ScheduledPowerOffState
        self.state.scheduled = False
        self.ready_to_turn_off : Callable = self.__create_ready_to_turn_off_condition(printer, temperature_threshold)
        self.event_manager = event_manager
        self.timer = None

    def __get_print_finished_events(self):
        """
        All events regarding the finishing of a print
        """
        return [
            self.octoprint.events.Events.PrintDone,
        ]

    def __get_events(self):
        """
        Return all the event's that should be subscribed to
        """
        return [
            self.TIMEOUT_EVENT,
            self.octoprint.events.Events.PrintStarted,
            *self.__get_print_finished_events(),
            Events.AUTOMATIC_POWER_OFF_DO_CHANGE_EVENT
        ]

    def __init_timer(self):
        """
        Initializes a new timer.

        @precondition: The current timer should be either not initialized
        or have exited in the past, since this doesn't dellocate resources
        """
        def post_timeout_events():
            self.event_manager.fire(
                event=self.TIMEOUT_EVENT,
            )
        if self.timer is None or self.timer.has_finished():
            self.timer = AsyncIntervalScheduler(post_timeout_events,timedelta(seconds=5))
        else:
            raise ValueError("Timer object first needs to be stopped before it's garbage collected")

    def enable(self):
        """
        Enable this feature.

        This is needed in order to schedule power offs
        """
        self.__init_timer()
        self.timer.start()
        self.__subscribe(
            events=self.__get_events(),
            callback=self.on_event
        )

    def disable(self):
        """
        Disable this feature.

        A scheduled power-off will automatically be unscheduled
        """
        # TODO is self.on_event the same as before ?
        self.__unsubscribe(
            events=self.__get_events(),
            callback=self.on_event
        )
        self.timer.stop()

    def __create_ready_to_turn_off_condition(self, printer: octoprint.printer.PrinterInterface, temperature_threshold):
        """
        Return a lambda that when called indicates that the printer is ready to be turned off
        """
        def condition():
            temp_data = printer.get_current_temperatures()
            return temp_data["bed"] < temperature_threshold and temp_data["tool"] < temperature_threshold

        return condition

    def on_event(self, event: octoprint.events.Events, payload):
        if event == self.TIMEOUT_EVENT:
            if self.state.scheduled and self.ready_to_turn_off():
                fire_power_state_do_change_event(
                    self.event_manager,
                    power_state=PowerState.OFF
                )
        elif event == octoprint.events.Events.PrintStarted:
            if self.state.scheduled:
                fire_automatic_power_off_do_change_event(
                    self.event_manager,
                    ScheduledPowerOffState(scheduled=False)
                )
        elif event in self.__get_print_finished_events():
            if self.state.scheduled:
                fire_automatic_power_off_do_change_event(
                    self.event_manager,
                    ScheduledPowerOffState(scheduled=True)
                )
        elif event == Events.AUTOMATIC_POWER_OFF_DO_CHANGE_EVENT():
            desired_state = api_scheduled_power_off_state_to_internal_repr(
                payload
            )
            if self.scheduled != desired_state.scheduled:
                self.state = desired_state
                fire_automatic_power_off_changed_event(
                    self.event_manager,
                    self.state
                )

    def __subscribe(self,events,callback):
        for event in events:
            self.event_manager.subscribe(event,callback)

    def __unsubscribe(self,events,callback):
        for event in events:
            self.event_manager.unsubscribe(event,callback)
