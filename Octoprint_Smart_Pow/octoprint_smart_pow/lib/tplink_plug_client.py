
import asyncio
from kasa import SmartPlug
from octoprint_smart_pow.lib.smart_plug_client import SmartPlugClient,PowerState


class TPLinkClient(SmartPlugClient):
    """
    Interface for a TPLink smart power plug.
    Implements the "PowerPlugClientInterface"
    """
    pass

    def __init__(self, smart_plug):
        self.plug = smart_plug

    def turn_on(self):
        asyncio.run(self.plug.turn_on())

    def turn_off(self):
        asyncio.run(self.plug.turn_off())

    def read(self) -> PowerState:
        self._refresh()
        return PowerState.ON if self.plug.is_on else PowerState.OFF

    def _refresh(self):
        """
        Refresh the internal plug object with it's real state

        Needs to be called before accessing properties for up-to-date data.
        """
        asyncio.run(self.plug.update())
