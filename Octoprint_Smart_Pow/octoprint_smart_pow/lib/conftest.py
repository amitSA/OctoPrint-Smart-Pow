from octoprint_smart_pow.lib.data.power_state import API_POWER_STATE_KEY
import pytest
from json import loads
from pathlib import Path
from kasa import SmartPlug
from kasa.tests.newfakes import FakeTransportProtocol
from octoprint_smart_pow.lib.tplink_plug_client import TPLinkPlug
import octoprint.plugin


@pytest.fixture
def api_power_state_off():
    return {API_POWER_STATE_KEY: "Off"}


@pytest.fixture
def api_power_state_on():
    return {API_POWER_STATE_KEY: "On"}


@pytest.fixture(scope="session")
def event_manager():
    octoprint.plugin.plugin_manager(init=True)
    event_manager = octoprint.events.EventManager()
    event_manager.fire(octoprint.events.Events.STARTUP)
    yield event_manager
    event_manager.fire(octoprint.events.Events.SHUTDOWN)


@pytest.fixture
def discovery_data():
    # XXX This file was sourced from https://github.com/python-kasa/python-kasa/blob/a468d520c0856debe171ceeb99aeb3d8ef91ba02/kasa/tests/fixtures/HS100(US)_1.0.json
    # It would be better to dynamically download this fixture file from the repo
    # as part of pytest setup.
    #    The commit should be pulled to the release-version that setup.py declares (and explicitly declare it in setup.py if the dep. isn't already)
    file = Path(__file__).parent / "tests" / "fixtures" / "HS100(US)_1.0.json"
    return loads(file.read_text())


@pytest.fixture
def fake_transport_protocol(discovery_data):
    return FakeTransportProtocol(info=discovery_data)


@pytest.fixture
def backing_smart_device(fake_transport_protocol) -> SmartPlug:
    plug = SmartPlug("127.0.0.1")
    plug.protocol = fake_transport_protocol
    return plug


@pytest.fixture
def tplink_plug_client(backing_smart_device):
    return TPLinkPlug(backing_smart_device)
