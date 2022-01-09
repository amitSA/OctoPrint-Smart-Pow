import unittest
import funcy
from octoprint_smart_pow.lib.features.power_state_writer import PowerStateWriter
import pytest
import octoprint
from octoprint.events import EventManager
from octoprint_smart_pow.lib.clock_utils import wait_untill
from octoprint_smart_pow.lib.data.events import Events
from octoprint_smart_pow.lib.data.power_state import PowerState
from octoprint_smart_pow.lib.tplink_plug_client import TPLinkPlug


class TestPowerStateWriter:

    @pytest.fixture
    def power_state_writer(
        self,
        tplink_plug_client,
        event_manager: EventManager
    ):
        return PowerStateWriter(
            plug=tplink_plug_client,
            event_manager=event_manager
        )

    @pytest.mark.asyncio
    async def test_read_and_write_power_state(
        self,
        power_state_writer,
        event_manager : EventManager,
        tplink_plug_client : TPLinkPlug,
        api_power_state_off,
        api_power_state_on,
        mocker,
    ):
        # register a mocker to listen to events so we can
        # make assertions on how the mocker was called
        event_listener = mocker.Mock()
        event_manager.subscribe(
            Events.POWER_STATE_CHANGED_EVENT(),
            event_listener
        )
        # partially construct an assertion function for
        # receiving the confirmation event
        wait_for_event = funcy.partial(
            self.wait_for_event,
            listener=event_listener,
            mocker=mocker
        )

        # set initial state
        await tplink_plug_client.turn_on()

        # turn off
        event_manager.fire(
            event=Events.POWER_STATE_DO_CHANGE_EVENT(),
            payload=api_power_state_off
        )
        # wait for state change event for "off" to come
        wait_for_event(
            event=Events.POWER_STATE_CHANGED_EVENT(),
            expected_payload=api_power_state_off,
        )
        assert await tplink_plug_client.read() == PowerState.OFF

        # turn on
        event_manager.fire(
            event=Events.POWER_STATE_DO_CHANGE_EVENT(),
            payload=api_power_state_on
        )
        # wait for state change event for "on" to come
        wait_for_event(
            event=Events.POWER_STATE_CHANGED_EVENT(),
            expected_payload=api_power_state_on,
        )
        assert await tplink_plug_client.read() == PowerState.ON

    def wait_for_event(
        self,
        event : octoprint.events.Events,
        expected_payload,
        listener: unittest.mock.Mock,
        mocker,
    ):
        def event_received_with_payload():
            return mocker.call(event,expected_payload) in listener.call_args_list

        wait_untill(
            condition=event_received_with_payload,
            condition_name=f"event {event} received with expected payload"
        )
