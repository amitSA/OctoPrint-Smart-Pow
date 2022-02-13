import asyncio
from kasa.tests.newfakes import FakeTransportProtocol
from octoprint.events import EventManager
from octoprint_smart_pow.lib.data.events import Events
from octoprint_smart_pow.lib.data.power_state import PowerState
import logging
from octoprint_smart_pow.lib.event_manager_helpers import (
    fire_power_state_changed_event,
)

from octoprint_smart_pow.lib.mappers.power_state import (
    api_power_state_to_internal_repr,
)
from octoprint_smart_pow.lib.thread_utils import run_in_thread
from octoprint_smart_pow.lib.tplink_plug_client import TPLinkPlug


class PowerStateWriter:
    """
    Read and write power state using events.
    """

    def __init__(
        self, plug: TPLinkPlug, event_manager: EventManager, logger=logging
    ):
        self.event_manager = event_manager
        self.event_manager.subscribe(
            Events.POWER_STATE_DO_CHANGE_EVENT(), self.change_power_state
        )
        self.plug = plug
        self.logger = logger
        self.current_state: PowerState = PowerState.UNKNOWN

    def get_state(self) -> PowerState:
        return self.current_state

    def change_power_state(self, event, payload):
        desired_state: PowerState = api_power_state_to_internal_repr(payload)
        self.__set_power_state_of_external_device(desired_state)

    # TODO maybe to better indicate in the calling thread, re-raise exceptions
    # from the worker thread ?
    @run_in_thread
    def __set_power_state_of_external_device(self, power_state: PowerState):
        # Clone the plug in order to use this on a new asyncio thread
        plug = self.__clone_plug(self.plug)
        self.logger.info("Issuing turning plug '%s'", power_state.name)
        TIMEOUT_SECS = 10
        if power_state == PowerState.ON:
            asyncio.run(asyncio.wait_for(plug.turn_on(), TIMEOUT_SECS))
        elif power_state == PowerState.OFF:
            asyncio.run(asyncio.wait_for(plug.turn_off(), TIMEOUT_SECS))
        else:
            raise ValueError(f"power_state {power_state} unrecognized")
        fire_power_state_changed_event(self.event_manager, power_state)
        self.logger.info("Finished turning plug '%s'", power_state.name)

    # TODO Generalize to all smart plugs. Offload cloning to the sub-class
    def __clone_plug(self, tp_plug: TPLinkPlug):
        """
        Return a clone of a smart plug.
        """
        cloned_tp_plug = TPLinkPlug(host=tp_plug.plug.host, logger=self.logger)
        # Makes this class testable so the cloned plug
        # uses the same mocked backend, and doesn't actually connect to that host
        if isinstance(tp_plug.plug.protocol, FakeTransportProtocol):
            cloned_tp_plug.plug.protocol = tp_plug.plug.protocol
        return cloned_tp_plug
