
"""
Find smart plug clients
"""
import asyncio
from funcy import retry, lfilter
from octoprint_smart_pow.lib.tplink_plug_client import TPLinkClient
from kasa import Discover
import logging

class NoDevicesFoundError(Exception):
    """Indicates that no smart power devices were found on the network"""
    pass

@retry(tries=3,errors=NoDevicesFoundError,timeout=5)
def find_tp_link_plug(alias,logger=logging) -> TPLinkClient:
    devices = asyncio.run(Discover.discover())
    # XXX can prob use funcy method to select an object from a list that contains a specific property
    def matches_alias(device):
        return device.alias == alias
    matched_devices = lfilter(matches_alias, devices.values())
    if len(matched_devices) == 0:
        logger.info("No matched devices were found")
        raise NoDevicesFoundError()

    return TPLinkClient(matched_devices[0])


if __name__ == "__main__":
    """Manual tests"""
    plug = find_tp_link_plug("3d printer power plug")
    plug.turn_on()
    print(plug.read())