import pytest
from json import loads
from pathlib import Path
from kasa import SmartPlug
from kasa.tests.newfakes import FakeTransportProtocol
import logging
import asyncio
from octoprint_smart_pow.lib.data.power_state import PowerState
from octoprint_smart_pow.lib.tplink_plug_client import TPLinkPlug


@pytest.mark.asyncio
class TestTPLinkPlugClient:

    # XXX it would be better to implement this precondition that some tests
    # have as a decorator on each test-case.  This is more explicit rather than on
    # reliying on a unit-test
    async def test_device_is_initialized_to_be_off(
        self, backing_smart_device: SmartPlug
    ):
        """
        Make sure the device starts out in the "off" power state
        Some unit-tests depend on this precondition
        """
        await backing_smart_device.update()
        is_on = backing_smart_device.is_on
        assert is_on is False

    async def test_read_power_state(self, tplink_plug_client):
        """Test whether we can read the correct power state"""
        assert await tplink_plug_client.read() is PowerState.OFF

    async def test_set_power_state(self, tplink_plug_client: TPLinkPlug):
        """Test whether we can set the power state"""
        await tplink_plug_client.turn_on()
        assert await tplink_plug_client.read() is PowerState.ON

    async def test_read_power_state_after_external_change(
        self, tplink_plug_client, backing_smart_device: SmartPlug
    ):
        """Test whether we read the correct power state after another system changes it"""
        # this simulates an external system changing the device's power state
        # (versus the client doing it)
        await backing_smart_device.turn_on()
        assert await tplink_plug_client.read() is PowerState.ON
