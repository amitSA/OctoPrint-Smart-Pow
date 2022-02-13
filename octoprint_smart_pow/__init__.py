# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import asyncio
import time
import octoprint.plugin
from octoprint_smart_pow.lib.data.automatic_power_off import (
    AUTOMATIC_POWER_OFF_SCHEDULED_API_KEY,
    AUTOMATIC_POWER_OFF_API_COMMAND,
)
from octoprint_smart_pow.lib.data.power_state import (
    PowerState,
)
from octoprint_smart_pow.lib.data.events import Events
from octoprint_smart_pow.lib import events
from octoprint_smart_pow.lib.event_manager_helpers import (
    fire_automatic_power_off_do_change_event,
    fire_power_state_changed_event,
)
from octoprint_smart_pow.lib.features.automatic_power_off import (
    AutomaticPowerOff,
)
from octoprint_smart_pow.lib.features.power_state_writer import PowerStateWriter
from octoprint_smart_pow.lib.features.power_state_publisher import (
    PowerStatePublisher,
)
from octoprint_smart_pow.lib import discoverer
from octoprint.events import EventManager

import octoprint.plugin
import flask
from octoprint_smart_pow.lib.features.printer_shutdown_predicate import (
    printer_ready_to_shutdown,
)
from octoprint_smart_pow.lib.mappers.automatic_power_off import (
    api_scheduled_power_off_state_to_internal_repr,
    scheduled_power_off_state_to_api_repr,
)

from octoprint_smart_pow.lib.mappers.power_state import (
    power_state_to_api_repr,
    api_power_state_to_internal_repr,
)
from octoprint_smart_pow.lib.data.power_state import (
    API_POWER_STATE_KEY,
    POWER_STATE_DO_CHANGE_API_COMMAND,
    APIPowerState,
)
from octoprint_smart_pow.lib.thread_utils import run_in_thread
from octoprint_smart_pow.lib.tplink_plug_client import TPLinkPlug
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
        self.power_publisher = None

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

        # initialize power controller
        self.power_state_writer = PowerStateWriter(
            plug=self.tp_smart_plug,
            event_manager=self.event_manager,
            logger=self._logger,
        )

        self.automatic_power_off = AutomaticPowerOff(
            self.event_manager,
            funcy.partial(printer_ready_to_shutdown, self._printer),
        )
        self.automatic_power_off.enable()  # TODO: Instead of being hard-coded, we want it controlled by the UI

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
            Events.POWER_STATE_CHANGED_EVENT(),
            Events.AUTOMATIC_POWER_OFF_CHANGED_EVENT(),
        ]
        # the order of these operations matter
        Events.set_prefix(f"plugin_smart_pow")
        return custom_events

    def on_event(self, event: str, payload):
        if event == Events.AUTOMATIC_POWER_OFF_CHANGED_EVENT():
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
        return dict(js=["js/smart_pow.js"])

    # Simple API Plugin Implementation

    def get_api_commands(self):
        return {
            # Each field is the list of all property names this command takes
            # This command is a proxy for the respective event
            POWER_STATE_DO_CHANGE_API_COMMAND: [API_POWER_STATE_KEY],
            AUTOMATIC_POWER_OFF_API_COMMAND: [
                AUTOMATIC_POWER_OFF_SCHEDULED_API_KEY
            ],
        }

    def on_api_command(self, command, data):
        """
        Defining POST route
        """
        import flask  # TODO DO I NEED THIS ?

        # TODO What happens if an exception happens ? Do I need to setup a flask error response
        if command == POWER_STATE_DO_CHANGE_API_COMMAND:
            self.event_manager.fire(
                Events.POWER_STATE_DO_CHANGE_EVENT(), payload=data
            )
        elif command == AUTOMATIC_POWER_OFF_API_COMMAND:
            fire_automatic_power_off_do_change_event(
                api_scheduled_power_off_state_to_internal_repr(data)
            )
        else:
            raise ValueError(f"command {command} is unrecognized")

    def on_api_get(self, request):
        """
        Defining GET route

        Return all relevant data structures since there can only be one GET
        implemented by the SimpleAPIPlugin
        """
        # Wait for dependencies to be defined by startup
        # XXX hacky
        while self.power_publisher is None:
            time.sleep(1)

        api_power_state: APIPowerState = power_state_to_api_repr(
            self.power_publisher.get_state()
        )
        automatic_power_off = scheduled_power_off_state_to_api_repr(
            self.automatic_power_off.get_state()
        )
        return flask.jsonify({**api_power_state, **automatic_power_off})


plugin = SmartPowPlugin()

global __plugin_implementation__
__plugin_implementation__ = SmartPowPlugin()

global __plugin_pythoncompat__
__plugin_pythoncompat__ = ">=2.7,<4"

global __plugin_hooks__
__plugin_hooks__ = {
    "octoprint.events.register_custom_events": plugin.register_custom_events
}
