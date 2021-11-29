import pytest
import asyncio
import octoprint.events
from octoprint_smart_pow.lib.data.power_state_changed_event import (
    PowerState
)

from kasa import SmartPlug
from octoprint_smart_pow.lib.tplink_plug_client import TPLinkClient
from octoprint_smart_pow.lib import events
from datetime import timedelta
import time
from octoprint_smart_pow.lib.clock_utils import wait_untill



class TestPowerStatePublisher:

    @pytest.fixture
    def event_manager(self):
        # XXX double check how to cleanup resources since this is a mult-threaded object
        #     I think it might be as simple as sending an "octoprint_shutdown" event.
        event_manager = octoprint.events.EventManager()
        event_manager.fire(octoprint.events.Events.STARTUP)
        yield event_manager
        event_manager.fire(octoprint.events.Events.SHUTDOWN)


    def test_publish_power_state_changed_event(self,
        event_manager,
        plug_client: TPLinkClient,
        backing_smart_device: SmartPlug,
        mocker):
        """
        Tests whether "POWER_STATE_CHANGED_EVENT" events will be thrown
        when the power state is changed
        """
        # double check initial state is off for making sure we're starting off at a known state
        assert plug_client.read() == PowerState.OFF

        @mocker
        def subscriber(event, payload):
            pass

        def condition(payload):
            return subscriber.called_with() == (events.POWER_STATE_CHANGED_EVENT,OFF_PAYLOAD)

        event_manager.subscribe(events.POWER_STATE_CHANGED_EVENT,callback=subscriber)
        # Simulate an external device turn-off
        asyncio.run(backing_smart_device.turn_off())
        # Wait for the subscriber to be called
        # XXX shorten these intervals
        wait_untill(condition,poll_period=timedelta(seconds=1), timeout=timedelta(seconds=5))



        # Psudeo Code
        # assert initial state of off
        # subscribe for POWER_STATE_CHANGED_EVENT events
        # changing backing_devices state to on
        # wait X seconds for subscriber to receive "POWER_STATE_CHANGED_EVENT" on event
        # changing backing_devices state to off
        # wait X seconds for subscriber to receive "POWER_STATE_CHANGED_EVENT" off event
