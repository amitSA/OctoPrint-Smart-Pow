
import pytest
from json import loads
from pathlib import Path
from kasa import SmartPlug
from kasa.tests.newfakes import FakeTransportProtocol
import logging
import asyncio
from octoprint_smart_pow.lib.smart_plug_client import SmartPlugClient,PowerState
from octoprint_smart_pow.lib.tplink_plug_client import TPLinkClient

class TestTPLinkPlugClient:

    @pytest.fixture
    def discovery_data(self):
        # XXX This file was sourced from https://github.com/python-kasa/python-kasa/blob/a468d520c0856debe171ceeb99aeb3d8ef91ba02/kasa/tests/fixtures/HS100(US)_1.0.json
        # It would be better to dynamically download this fixture file from the repo
        # as part of pytest setup.
        #    The commit should be pulled to the release-version that setup.py declares (and explicitly declare it in setup.py if the dep. isn't already)
        file = Path(__file__).parent / "fixtures" / "HS100(US)_1.0.json"
        return loads(file.read_text())

    @pytest.fixture
    def fake_transport_protocol(self,discovery_data):
        return FakeTransportProtocol(info=discovery_data)

    @pytest.fixture
    def mocked_smart_device(self, fake_transport_protocol) -> SmartPlug:
        plug = SmartPlug("127.0.0.1")
        plug.protocol = fake_transport_protocol
        return plug

    @pytest.fixture
    def plug_client(self, mocked_smart_device):
        return TPLinkClient(mocked_smart_device)

    # XXX it would be better to implement this precondition that some tests
    # have as a decorator on each test-case.  This is more explicit rather than on
    # reliying on a unit-test
    def test_device_is_initialized_to_be_off(self,mocked_smart_device: SmartPlug):
        """
        Make sure the device starts out in the "off" power state
        Some unit-tests depend on this precondition
        """
        asyncio.run(mocked_smart_device.update())
        is_on = mocked_smart_device.is_on
        assert is_on is False

    def test_read_power_state(self,plug_client):
        """Test whether we can read the correct power state"""
        assert plug_client.read() is PowerState.OFF

    def test_set_power_state(self,plug_client: TPLinkClient):
        """Test whether we can set the power state"""
        plug_client.turn_on()
        assert plug_client.read() is PowerState.ON

    def test_read_power_state_after_external_change(self,plug_client, mocked_smart_device: SmartPlug):
        """Test whether we read the correct power state after another system changes it"""
        # this simulates an external system changing the device's power state
        # (versus the client doing it)
        asyncio.run(mocked_smart_device.turn_on())
        assert plug_client.read() is PowerState.ON
