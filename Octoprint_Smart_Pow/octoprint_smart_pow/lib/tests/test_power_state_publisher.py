from octoprint_smart_pow.lib.power_state_publisher import PowerStatePublisher
import pytest
import asyncio
import octoprint.events
import octoprint.plugin
from octoprint_smart_pow.lib.data.power_state_changed_event import (
    PowerState,
    POWER_STATE_CHANGED_EVENT,
    PowerStateChangedEventPayload
)

from kasa import SmartPlug
from octoprint_smart_pow.lib.tplink_plug_client import TPLinkClient
from datetime import timedelta
import time
from octoprint_smart_pow.lib.clock_utils import wait_untill


OFF_PAYLOAD = PowerStateChangedEventPayload(power_state=PowerState.OFF)
ON_PAYLOAD = PowerStateChangedEventPayload(power_state=PowerState.ON)

# XXX tag this test as a "long_test" since it takes more than 1 second to complete.
class TestPowerStatePublisher:

    @pytest.fixture
    def event_manager(self):
        octoprint.plugin.plugin_manager(init=True)
        event_manager = octoprint.events.EventManager()
        event_manager.fire(octoprint.events.Events.STARTUP)
        yield event_manager
        event_manager.fire(octoprint.events.Events.SHUTDOWN)

    @pytest.fixture(autouse=True)
    def power_state_change_publisher(self,event_manager,tplink_plug_client: TPLinkClient):
        change_publisher = PowerStatePublisher(event_manager,tplink_plug_client)
        change_publisher.start()
        yield
        change_publisher.stop()

    def test_publish_power_state_changed_events_from_off_on_off_on(self,
        event_manager : octoprint.events.EventManager,
        tplink_plug_client: TPLinkClient,
        backing_smart_device: SmartPlug,
        mocker):
        """
        Tests whether "POWER_STATE_CHANGED_EVENT" events will be thrown
        when the power state is changed
        """
        # double check initial state is off for making sure we're starting off at a known state
        assert tplink_plug_client.read() == PowerState.OFF

        # XXX can I pass in a spec to describe that subscriber takes in an (event,payload) arg signature ?
        #  And as an extra safe-guard if for some reason extra arguments are passed into the function ?
        subscriber = mocker.Mock()
        def create_condition(expected_payload: PowerStateChangedEventPayload):
            def condition():
                return subscriber.call_args == mocker.call(POWER_STATE_CHANGED_EVENT,expected_payload)
            return condition

        event_manager.subscribe(event=POWER_STATE_CHANGED_EVENT,callback=subscriber)
        # Simulate an external device turn-on
        asyncio.run(backing_smart_device.turn_on())
        # Wait for the subscriber to be called
        wait_untill(condition=create_condition(ON_PAYLOAD),poll_period=timedelta(seconds=1),timeout=timedelta(seconds=10),condition_name="Power is On")

        # Simulate an external device turn-off
        asyncio.run(backing_smart_device.turn_off())
        wait_untill(condition=create_condition(OFF_PAYLOAD),poll_period=timedelta(seconds=1),timeout=timedelta(seconds=10),condition_name="Power is Off")