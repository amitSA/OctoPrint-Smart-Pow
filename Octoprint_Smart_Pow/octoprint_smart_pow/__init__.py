# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import asyncio
import octoprint.plugin
from octoprint_smart_pow.lib.data.conditional_off import CONDITIONAL_POWER_OFF_API_KEY, CONDITIONAL_POWER_OFF_API_COMMAND
from octoprint_smart_pow.lib.data.power_state import (
    PowerState,
)
from octoprint_smart_pow.lib.data.events import Events
from octoprint_smart_pow.lib import events
from octoprint_smart_pow.lib.event_manager_helpers import fire_power_state_changed_event
from octoprint_smart_pow.lib.power_state_publisher import PowerStatePublisher
from octoprint_smart_pow.lib import discoverer
from octoprint.events import EventManager

import octoprint.plugin
import flask

from octoprint_smart_pow.lib.mappers.power_state import (
    power_state_to_api_repr,
    api_power_state_to_internal_repr
)
from octoprint_smart_pow.lib.data.power_state import (
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
        # TODO Octoprint docs say to not perform long-running or blocking operations in this hook,
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
        # Turn off the conditional power off feature by default
        # It will automatically get turned on by the UI after a print finishes
        self.__set_conditional_power_off(enable=False)



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
        custom_events = [
            Events.POWER_STATE_CHANGED_EVENT_NAME(),
            Events.CONDITIONAL_POWER_OFF_ENABLED_EVENT_NAME()
        ]
        # the order of these operations matter
        Events.set_prefix(f"plugin_smart_pow")
        return custom_events

    def on_event(self, event: str, payload):
        if event == Events.POWER_STATE_CHANGED_EVENT_NAME():
            self._logger.info(f"Received event '{event}'")
            changed_state: PowerState = api_power_state_to_internal_repr(payload)
            # Once we remove GET power_state from the api, we don't even need this field
            self.power_state = changed_state
            # self._settings.save() # Older code for saving to yaml.  Can remove
        if event == Events.CONDITIONAL_POWER_OFF_ENABLED_EVENT_NAME():
            self._logger.info(f"Received event '{event}'")
            self.cond_power_off = payload

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
            API_POWER_STATE_SET_COMMAND:[API_POWER_STATE_KEY],
            CONDITIONAL_POWER_OFF_API_COMMAND: [CONDITIONAL_POWER_OFF_API_KEY]
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
        import flask # TODO DO I NEED THIS ?
        # TODO catch possible errors and return proper error codes, instead of just the
        # letting the thread fail.  Look at the SimpleAPI docs, there might be a easy way to
        # define error handlers
        plug = TPLinkClient(host=self.tp_smart_plug.plug.host, logger=self._logger)
        if command == API_POWER_STATE_SET_COMMAND:
            power_state = api_power_state_to_internal_repr(data)
            self.__set_power_state_of_external_device(plug, power_state)
        elif command == CONDITIONAL_POWER_OFF_API_COMMAND:
            # TODO I might want to create a mapper to do this
            enable: bool = data[CONDITIONAL_POWER_OFF_API_KEY]
            if enable is True:
                raise ValueError(f"cannot enable conditional_off from UI")
            self.__set_conditional_power_off(enable=enable)
        else:
            raise ValueError(f"command {command} is unrecognized")



    # TODO: change the type of plug to SmartDevice so this code can extend to other smart devices
    def __set_power_state_of_external_device(self, plug: TPLinkClient, power_state: PowerState):
        self._logger.info("Issuing turning plug '%s'",power_state.name)
        TIMEOUT_SECS = 10
        if power_state == PowerState.ON:
            asyncio.run(
                asyncio.wait_for(plug.turn_on(),TIMEOUT_SECS)
            )
        elif power_state == PowerState.OFF:
            asyncio.run(
                asyncio.wait_for(plug.turn_off(),TIMEOUT_SECS)
            )
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
            api_power_state
        )

    # Conditional_Off stuff
    def __set_conditional_power_off(self, enable: bool):
        """
        Set the conditional_power_off feature to either on or off

        params
        enable: True will turn it on and False will turn it off
        """
        # TODO Internally turn off or on
        self.event_manager.fire(
            Events.CONDITIONAL_POWER_OFF_ENABLED_EVENT_NAME(),
            enable
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
