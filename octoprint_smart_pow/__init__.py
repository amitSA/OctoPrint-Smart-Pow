# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import asyncio
import time
import octoprint.plugin
from octoprint_smart_pow.lib.data.automatic_power_off import (
    AUTOMATIC_POWER_OFF_SCHEDULED_API_KEY,
    AUTOMATIC_POWER_OFF_API_COMMAND,
    UnscheduledPowerOff,
)
from octoprint_smart_pow.lib.data.power_state import (
    PowerState,
)
from octoprint_smart_pow.lib.data.events import Events
# from octoprint_smart_pow.lib import events
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
    scheduled_power_off_state_to_api_repr,
)
from octoprint_smart_pow.lib.mappers.events import fire_event

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
    def on_after_startup(self):
        self._logger.info("Starting up Smart Pow Plugin")
        self.event_manager: EventManager = self._event_bus
        self.power_state_writer = None
        self.power_state_publisher = None
        self.automatic_power_off = None
        tp_link_alias = self.get_setting("tp_link_smart_plug_alias")

        if tp_link_alias is not None:
            self.reset_power_state_publisher_and_writer(tp_link_alias)

        self.automatic_power_off = AutomaticPowerOff(
            self.event_manager,
            funcy.partial(printer_ready_to_shutdown, self._printer),
        )
        self.automatic_power_off.enable()  # TODO: Instead of being hard-coded, we want it controlled by the UI
        self._logger.info("Initialized Smart Pow plugin")

    def on_settings_save(self, data):
        tp_link_alias = data["tp_link_smart_plug_alias"]
        if self.get_setting("tp_link_smart_plug_alias") != tp_link_alias :
            # This method might take up to 30 seconds to complete, thus blocking
            # how long clicking "Save" in the UI will take.
            # We should give the user a heads up in the UI of that fact AND in the event
            # connecting fails, we should throw a popup in the UI
            self.reset_power_state_publisher_and_writer(tp_link_alias)

        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)

    # Needs to be run in it's own thread b/c when this is called by
    # Octoprint it's running in an event loop, but not called as an async
    # Since this function's dependencies need to run co-routines, they need
    # to be a in a thread that hasn't started an event loop yet
    @run_in_thread(wait=True)
    def reset_power_state_publisher_and_writer(self, tp_link_alias):
        tp_smart_plug = None
        try:
            tp_smart_plug = discoverer.find_tp_link_plug(
                    alias=tp_link_alias, logger=self._logger
                )
        except discoverer.NoDevicesFoundError:
            self._logger.error("No matched devices were found.")
        else:
            self.reset_power_state_writer(tp_smart_plug)
            self.reset_power_publisher(tp_smart_plug)

    def reset_power_state_writer(self, tp_smart_plug):
        if self.power_state_writer is not None and self.power_state_writer.started():
            self.power_state_writer.disable()

        self.power_state_writer = PowerStateWriter(
            plug=tp_smart_plug,
            event_manager=self.event_manager,
            logger=self._logger,
        )
        self.power_state_writer.enable()

    # TODO: Rename to power_state_publisher to be consistent with
    # power_state_writer
    def reset_power_publisher(self, tp_smart_plug):
        if self.power_state_publisher is not None and self.power_state_publisher.running():
            self.power_state_publisher.stop()

        self.power_state_publisher = PowerStatePublisher(
            event_manager=self.event_manager,
            smart_plug=tp_smart_plug,
            logger=self._logger,
        )
        self.power_state_publisher.start()

    def get_template_vars(self):
        """
        Injecting static values into templates

        Implemented by TemplatePlugin
        """
        return {
            "url": self.get_setting("url")
        }

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
            {"type": "navbar","custom_bindings": False},
            {"type": "settings","custom_bindings": False},
        ]

    def get_setting(self,*keys):
        """Return setting values"""
        return self._settings.get(list(keys))

    def get_settings_defaults(self):
        """
        Defines settings keys and their default values.
        """
        return {
            "tp_link_smart_plug_alias": "3d printer power plug",
            # "tp_link_smart_plug_alias": None,
            "automatic_shutdown": False,
            "automatic_shutdown_temp_threshold": "30",
            "url": "https://en.wikipedia.org/wiki/Forrest_Gump"
        }

    def on_shutdown(self):
        self.power_state_publisher.stop()

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
        # Wait for dependencies to be defined by startup
        # XXX hacky
        while self.event_manager is None:
            time.sleep(1)

        if command == POWER_STATE_DO_CHANGE_API_COMMAND:
            fire_event(
                self.event_manager,
                Events.POWER_STATE_DO_CHANGE_EVENT(),
                serialized_data=data
            )
        elif command == AUTOMATIC_POWER_OFF_API_COMMAND:
            fire_event(
                self.event_manager,
                Events.AUTOMATIC_POWER_OFF_DO_CHANGE_EVENT(),
                serialized_data=data
            )
        else:
            # TODO What happens if an exception happens ?
            # Do I need to setup a flask error response, or is that automatic ?
            raise ValueError(f"command {command} is unrecognized")

    def on_api_get(self, request):
        """
        Defining GET route

        Return all relevant data structures since there can only be one GET
        implemented by the SimpleAPIPlugin
        """
        api_power_state: APIPowerState = power_state_to_api_repr(
            self.power_state_publisher.get_state() if self.power_state_publisher is not None
            else PowerState.UNKNOWN
        )
        automatic_power_off = scheduled_power_off_state_to_api_repr(
            self.automatic_power_off.get_state() if self.automatic_power_off is not None
            else UnscheduledPowerOff
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
