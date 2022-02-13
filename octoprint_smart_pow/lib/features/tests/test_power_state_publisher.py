from octoprint_smart_pow.lib.data.events import Events
from octoprint_smart_pow.lib.features.power_state_publisher import (
    PowerStatePublisher,
)
import pytest
import asyncio
import octoprint.events
import octoprint.plugin
from octoprint_smart_pow.lib.data.power_state import (
    API_POWER_STATE_KEY,
    APIPowerState,
    PowerState,
)

from kasa import SmartPlug
from octoprint_smart_pow.lib.tplink_plug_client import TPLinkPlug
from datetime import timedelta
import time
from octoprint_smart_pow.lib.wait_utils import wait_untill


# XXX tag this test as a "long_test" since it takes more than 1 second to complete.
class TestPowerStatePublisher:
    @pytest.fixture(autouse=True)
    def publisher(self, event_manager, tplink_plug_client: TPLinkPlug):
        publisher = PowerStatePublisher(event_manager, tplink_plug_client)
        publisher.start()
        yield publisher
        publisher.stop()

    @pytest.mark.asyncio
    async def test_publish_power_state_changed_events_from_off_on_off_on(
        self,
        event_manager: octoprint.events.EventManager,
        tplink_plug_client: TPLinkPlug,
        backing_smart_device: SmartPlug,
        api_power_state_off,
        api_power_state_on,
        mocker,
    ):
        """
        Tests whether "POWER_STATE_CHANGED_EVENT" events will be thrown
        when the power state is changed
        """
        # double check initial state is off for making sure we're starting off at a known state
        await tplink_plug_client.read() == PowerState.OFF

        # XXX can I pass in a spec to describe that subscriber takes in an (event,payload) arg signature ?
        #  And as an extra safe-guard if for some reason extra arguments are passed into the function ?
        subscriber = mocker.Mock()

        def create_condition(expected_payload: APIPowerState):
            def condition():
                return subscriber.call_args == mocker.call(
                    Events.POWER_STATE_CHANGED_EVENT(), expected_payload
                )

            return condition

        event_manager.subscribe(
            event=Events.POWER_STATE_CHANGED_EVENT(), callback=subscriber
        )
        # Simulate an external device turn-on
        await backing_smart_device.turn_on()
        # Wait for the subscriber to be called
        await wait_untill(
            condition=create_condition(api_power_state_on),
            poll_period=timedelta(seconds=1),
            timeout=timedelta(seconds=10),
            condition_name="Power is On",
        )

        # Simulate an external device turn-off
        await backing_smart_device.turn_off()
        await wait_untill(
            condition=create_condition(api_power_state_off),
            poll_period=timedelta(seconds=1),
            timeout=timedelta(seconds=10),
            condition_name="Power is Off",
        )
