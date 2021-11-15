# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import octoprint.plugin

class SmartPowPlugin(octoprint.plugin.StartupPlugin,
                       octoprint.plugin.TemplatePlugin,
                       octoprint.plugin.SettingsPlugin,
                       octoprint.plugin.AssetPlugin):
    def on_after_startup(self):
        self._logger.info("Starting up Smart Pow Plugins")
        self._logger.info(f"settings url: {self._settings.get(['url'])}")

    def get_settings_defaults(self):
        """
        Defines settings keys and their default values.
        """
        return {
        "power_plug_state": False,
        }

    def get_template_vars(self):
        """Implemented by the TemplatePlugin for injecting static values"""
        return dict(power_plug_state=self._settings.get(["power_plug_state"]))

    # def get_template_configs(self):
    #     """
    #     Return a list of configurations for each template
    #     Each configuration describes properties about the injection of the template.
    #     """
    #     return [
    #         # "type" is the primary key, since by default each type uniquely maps to a specifically named template file
    #         {"type":"navbar","custom_bindings":False},
    #         {"type":"settings","custom_bindings":False},
    #     ]

    # def get_assets(self):
    #     """
    #     Used by the asset plugin to register custom view models.
    #     """
    #     return dict(
    #     js=["js/helloworld.js"]
    #     )

__plugin__name__ = "SmartPow"
__plugin_pythoncompat__ = ">=2.7,<4"
__plugin_implementation__ = SmartPowPlugin()