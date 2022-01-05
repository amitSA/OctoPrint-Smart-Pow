import asyncio
from kasa import SmartPlug
from octoprint_smart_pow.lib.smart_plug_client import SmartPlugClient
from octoprint_smart_pow.lib.data.power_state import PowerState
import logging

# TODO: rename this file to tplink_plug to resemble the new name
class TPLinkPlug(SmartPlugClient):
    """
    Interface for a TPLink smart power plug.
    Implements the "PowerPlugClientInterface"
    """

    pass

    def __init__(
        self, smart_plug: SmartPlug = None, host: str = None, logger=logging
    ):
        """
        Create a plug client either from a kasa SmartPlug object or the host ip
        """
        # If initialized via host, the docs say we need to update() the plug first
        self.needs_initial_async_update = False
        if smart_plug is not None:
            self.plug = smart_plug
        else:
            if host is None:
                raise ValueError(
                    "Host needs to be non-None if smart_plug is None"
                )
            self.plug = SmartPlug(host=host)
            self.needs_initial_async_update = True
        self.logger = logger

    async def turn_on(self):
        if self.needs_initial_async_update:
            await self.plug.update()
            self.needs_initial_async_update = False

        await self.plug.turn_on()

    async def turn_off(self):
        if self.needs_initial_async_update:
            await self.plug.update()
            self.needs_initial_async_update = False

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
