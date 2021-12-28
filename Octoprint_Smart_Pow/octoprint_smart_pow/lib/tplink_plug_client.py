import asyncio
from kasa import SmartPlug
from octoprint_smart_pow.lib.smart_plug_client import SmartPlugClient
from octoprint_smart_pow.lib.data.power_state_changed_event import PowerState
import logging


class TPLinkClient(SmartPlugClient):
    """
    Interface for a TPLink smart power plug.
    Implements the "PowerPlugClientInterface"
    """

    pass

    def __init__(self, smart_plug: SmartPlug, logger=logging):
        self.plug = smart_plug
        self.logger = logger

    async def turn_on(self):
        await self.plug.turn_on()

    async def turn_off(self):
        await self.plug.turn_off()

    async def read(self) -> PowerState:
        """
        Asynchronously read the current power state
        """
        await self.plug.update()
        return PowerState.ON if self.plug.is_on else PowerState.OFF

    def _refresh(self):
        """
        Refresh the internal plug object with it's real state

        Needs to be called before accessing properties for up-to-date data.
        """
        asyncio.run(self.plug.update())
        # self.logger.info("Is event loop open %b",not asyncio.get_event_loop().is_closed())
