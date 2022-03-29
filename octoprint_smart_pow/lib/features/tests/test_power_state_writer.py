import unittest
import funcy
from funcy import last
from octoprint_smart_pow.lib.features.power_state_writer import PowerStateWriter
import pytest
import octoprint
from octoprint.events import EventManager
from octoprint_smart_pow.lib import wait_utils
from octoprint_smart_pow.lib.data.events import Events
from octoprint_smart_pow.lib.data.power_state import PowerState
from octoprint_smart_pow.lib.tplink_plug_client import TPLinkPlug


class TestPowerStateWriter:
    @pytest.fixture
    def power_state_writer(
        self, tplink_plug_client, event_manager: EventManager
    ):
        return PowerStateWriter(
            plug=tplink_plug_client, event_manager=event_manager
        )

    @pytest.mark.asyncio
    async def test_write_power_state(
        self,
        power_state_writer,
        event_manager: EventManager,
        tplink_plug_client: TPLinkPlug,
        api_power_state_off,
        api_power_state_on,
        mocker,
    ):
        power_state_writer.enable()
        # register a mocker to listen to events so we can
        # make assertions on how the mocker was called
        event_listener = mocker.Mock()
        event_manager.subscribe(
            Events.POWER_STATE_CHANGED_EVENT(), event_listener
        )
        # partially construct an assertion function for
        # receiving the confirmation event
        wait_untill_event = funcy.partial(
            wait_utils.wait_untill_event,
            event_manager=event_manager,
        )

        # set initial state
        await tplink_plug_client.turn_on()

        # turn off
        event_manager.fire(
            event=Events.POWER_STATE_DO_CHANGE_EVENT(),
            payload=api_power_state_off,
        )
        # wait for state change event for "off" to come
        await wait_untill_event(
            event=Events.POWER_STATE_CHANGED_EVENT(),
            payload=api_power_state_off,
        )
        assert await tplink_plug_client.read() == PowerState.OFF

        # turn on
        event_manager.fire(
            event=Events.POWER_STATE_DO_CHANGE_EVENT(),
            payload=api_power_state_on,
        )
        # wait for state change event for "on" to come
        await wait_untill_event(
            event=Events.POWER_STATE_CHANGED_EVENT(),
            payload=api_power_state_on,
        )
        assert await tplink_plug_client.read() == PowerState.ON

        # Test out that the writer does not change external plugs
        # when disabled
        power_state_writer.disable()

        # turn off power
        event_manager.fire(
            event=Events.POWER_STATE_DO_CHANGE_EVENT(),
            payload=api_power_state_off,
        )
        with pytest.raises(TimeoutError):
            await wait_untill_event(
                event=Events.POWER_STATE_CHANGED_EVENT(),
                payload=api_power_state_off,
            )
