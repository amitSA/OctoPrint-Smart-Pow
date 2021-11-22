# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import octoprint.plugin
from octoprint_smart_pow.lib.smart_plug_client import PowerState
from octoprint_smart_pow.lib import events
from octoprint_smart_pow.lib.power_state_publisher import PowerStatePublisher
from octoprint_smart_pow.lib import discoverer
from octoprint.events import EventManager

class SmartPowPlugin(octoprint.plugin.StartupPlugin,
                       octoprint.plugin.TemplatePlugin,
                       octoprint.plugin.SettingsPlugin,
                       octoprint.plugin.AssetPlugin):


    def on_after_startup(self):
        self._logger.info("Starting up Smart Pow Plugin")
        self._logger.info("Discovering TP-Link smart plug device in the home network")
        # XXX Octoprint docs say to not perform long-running or blocking operations in this hook,
        # yet this method can take up to 15 seconds to resolve.
        # reference: https://docs.octoprint.org/en/master/plugins/mixins.html#octoprint.plugin.StartupPlugin.on_after_startup
        tp_smart_plug = discoverer.find_tp_link_plug(alias=self.__smart_plug_alias_setting(), logger=self._logger)
        self.event_manager : EventManager = self._event_bus
        self.power_publisher = PowerStatePublisher(
            event=events.POWER_STATE_CHANGED,
            event_manager=self.event_manager,
            smart_plug=tp_smart_plug)

        self.power_publisher.start()

        self.event_manager.subscribe(event=events.POWER_STATE_CHANGED,callback=self.on_power_status_change)


    def get_settings_defaults(self):
        """
        Defines settings keys and their default values.
        """
        return {
            "power_plug_state": False,
            "tp_link_smart_plug_alias": "3d printer power plug"
        }

    def get_template_vars(self):
        """
        Injecting static values into templates

        Implemented by TemplatePlugin
        """
        return dict(power_plug_state=self._settings.get(["power_plug_state"]))


    def register_custom_events(self):
        return [
            events.POWER_STATE_CHANGED
        ]

    def on_power_status_change(self, event: str, payload: any):
        self._logger.info(f"Received event {event}")
        changed_state : PowerState = payload["power_state"]
        if changed_state == PowerState.OFF:
            self._settings.set(["power_plug_state"],"off")
        else:
            self._settings.set(["power_plug_state"],"on")

    def get_template_configs(self):
        """
        Return a list of configurations for each template
        Each configuration describes properties about the injection of the template.
        """
        return [
            # "type" is the primary key, since by default each type uniquely maps to a specifically named template file
            {"type":"navbar","custom_bindings":False},
        ]

    def __smart_plug_alias_setting(self):
        """Return the alias of the tp-link smart_plug to connect to"""
        return self._settings.get(["tp_link_smart_plug_alias"])

    # def get_assets(self):
    #     """
    #     Used by the asset plugin to register custom view models.
    #     """
    #     return dict(
    #     js=["js/helloworld.js"]
    #     )

plugin = SmartPowPlugin()

global __plugin_implementation__
__plugin_implementation__ = SmartPowPlugin()

global __plugin_pythoncompat__
__plugin_pythoncompat__ = ">=2.7,<4"

global __plugin_hooks__
__plugin_hooks__ = {
    "octoprint.events.register_custom_events": plugin.register_custom_events
}