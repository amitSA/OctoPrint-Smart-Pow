
"""
Find smart plug clients
"""
import asyncio
from octoprint_smart_pow.lib.tplink_plug_client import TPLinkClient
from kasa import Discover


def find_tp_link_plug(alias) -> TPLinkClient:
    devices = asyncio.run(Discover.discover())
    # XXX can prob use funcy method to select an object from a list that contains a specific property
    def matches_alias(device):
        return device.alias == alias
    device = next(filter(matches_alias, devices.values()))
    return TPLinkClient(device)


if __name__ == "__main__":
    plug = find_tp_link_plug("3d printer power plug")
    plug.turn_on()
    print(plug.read())