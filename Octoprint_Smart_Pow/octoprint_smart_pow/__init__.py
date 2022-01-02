# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import asyncio
import octoprint.plugin
from octoprint_smart_pow.lib.data.power_state_changed_event import (
    PowerStateChangedEventPayload,
    POWER_STATE_CHANGED_EVENT,
    PowerState,
)
from octoprint_smart_pow.lib import events
from octoprint_smart_pow.lib.power_state_helpers import fire_power_state_changed_event
from octoprint_smart_pow.lib.power_state_publisher import PowerStatePublisher
from octoprint_smart_pow.lib import discoverer
from octoprint.events import EventManager

import octoprint.plugin
import flask

from octoprint_smart_pow.lib.mappers.power_state import (
    power_state_to_api_repr,
    api_power_state_to_internal_repr
)
from octoprint_smart_pow.lib.data.power_state_api import (
    API_POWER_STATE_KEY,
    API_POWER_STATE_SET_COMMAND,
    APIPowerState
)
from octoprint_smart_pow.lib.tplink_plug_client import TPLinkClient
import threading
import funcy

class SmartPowPlugin(
    octoprint.plugin.StartupPlugin,
    octoprint.plugin.ShutdownPlugin,
    octoprint.plugin.TemplatePlugin,
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.EventHandlerPlugin,
    octoprint.plugin.SimpleApiPlugin,
):
    def __init__(self):
        self.power_state = PowerState.UNKNOWN

    # TODO: documentation for this hook says not to put long running tasks here
    # discoverer.find_tp_link_plug is a long running operation, I should probably
    # do this in a separate thread
    def on_after_startup(self):
        self._logger.info("Starting up Smart Pow Plugin")
        self._logger.info(
            "Discovering TP-Link smart plug device in the home network"
        )
        # XXX Octoprint docs say to not perform long-running or blocking operations in this hook,
        # yet this method can take up to 15 seconds to resolve.
        # reference: https://docs.octoprint.org/en/master/plugins/mixins.html#octoprint.plugin.StartupPlugin.on_after_startup
        self.tp_smart_plug = discoverer.find_tp_link_plug(
            alias=self.__smart_plug_alias_setting(), logger=self._logger
        )
        self.event_manager: EventManager = self._event_bus
        self.power_publisher = PowerStatePublisher(
            event_manager=self.event_manager,
            smart_plug=self.tp_smart_plug,
            logger=self._logger,
        )
        self.power_publisher.start()

        # find another instance to get around asyncio nonsense
        # self.tp_smart_plug = discoverer.find_tp_link_plug(
        #     alias=self.__smart_plug_alias_setting(), logger=self._logger
        # )


    def get_settings_defaults(self):
        """
        Defines settings keys and their default values.
        """
        return {
            "tp_link_smart_plug_alias": "3d printer power plug",
        }

    # def get_template_vars(self):
    #     """
    #     Injecting static values into templates

    #     Implemented by TemplatePlugin
    #     """
    #     return dict(power_plug_state=self._settings.get(["power_plug_state"]))

    def register_custom_events(self):
        return [POWER_STATE_CHANGED_EVENT]

    def on_event(self, event: str, payload: PowerStateChangedEventPayload):
        if event == POWER_STATE_CHANGED_EVENT:
            self._logger.info(f"Received event {event}")
            changed_state: PowerState = payload.power_state
            self.power_state = changed_state
            # self._settings.save() # Older code for saving to yaml.  Can remove

    def get_template_configs(self):
        """
        Return a list of configurations for each template
        Each configuration describes properties about the injection of the template.
        """
        return [
            # "type" is the primary key, since by default each type uniquely maps to a specifically named template file
            {"type": "tab", "custom_bindings": True},
        ]

    def __smart_plug_alias_setting(self):
        """Return the alias of the tp-link smart_plug to connect to"""
        return self._settings.get(["tp_link_smart_plug_alias"])

    def on_shutdown(self):
        self.power_publisher.stop()

    def get_assets(self):
        """
        Used by the asset plugin to register custom view models.
        """
        return dict(
            js=["js/smart_pow.js"]
        )

    # Simple API Plugin Implementation

    def get_api_commands(self):
        return {
            # each field is the list of all property names this command takes
            API_POWER_STATE_SET_COMMAND:[API_POWER_STATE_KEY]
        }

    @funcy.decorator
    def run_in_thread(call):
        t_worker = threading.Thread(target=call)
        t_worker.start()
        t_worker.join()

    @run_in_thread
    def on_api_command(self, command, data):
        """
        Defining POST route
        """
        import flask # DO I NEED THIS ?
        plug = TPLinkClient(host=self.tp_smart_plug.plug.host, logger=self._logger)
        if command == API_POWER_STATE_SET_COMMAND:
            state = APIPowerState(data[API_POWER_STATE_KEY])
            power_state : PowerState = api_power_state_to_internal_repr(state)
            self.__set_power_state_of_external_device(plug, power_state)
        else:
            raise ValueError(f"command {command} is unrecognized")



    # TODO: change the type of plug to SmartDevice so this code can extend to other smart devices
    def __set_power_state_of_external_device(self, plug: TPLinkClient, power_state: PowerState):
        if power_state == PowerState.ON:
            asyncio.run(plug.turn_on())
        elif power_state == PowerState.OFF:
            asyncio.run(plug.turn_off())
        else:
            raise ValueError(f"power_state {power_state} unrecognized")
        fire_power_state_changed_event(self.event_manager,power_state)
        self._logger.info("Finished turning plug '%s'",power_state.name)



    def on_api_get(self, request):
        """
        Defining GET route

        Return all relevant data structures since there can only be one GET
        implemented by the SimpleAPIPlugin
        """
        api_power_state : APIPowerState = power_state_to_api_repr(self.power_state)
        return flask.jsonify(
            **{API_POWER_STATE_KEY:api_power_state.value}
        )


plugin = SmartPowPlugin()

global __plugin_implementation__
__plugin_implementation__ = SmartPowPlugin()

global __plugin_pythoncompat__
__plugin_pythoncompat__ = ">=2.7,<4"

global __plugin_hooks__
__plugin_hooks__ = {
    "octoprint.events.register_custom_events": plugin.register_custom_events
}
