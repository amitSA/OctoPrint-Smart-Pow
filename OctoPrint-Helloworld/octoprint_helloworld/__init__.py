# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import octoprint.plugin

class HelloWorldPlugin(octoprint.plugin.StartupPlugin,
                       octoprint.plugin.TemplatePlugin,
                       octoprint.plugin.SettingsPlugin,
                       octoprint.plugin.AssetPlugin):
    def on_after_startup(self):
        self._logger.info("Sup World!")
        self._logger.info(f"settings url: {self._settings.get(['url'])}")

    def get_settings_defaults(self):
      return {
        "url":"https://en.wikipedia.org/wiki/Hello_world",
        "name": "Wikipedia",
      }

    def get_template_vars(self):
      """Implemented by the TemplatePlugin for injecting staticv values"""
      return dict(url=self._settings.get(["url"]))

    def get_template_configs(self):
      """
      Return a list of configurations for each template
      Each configuration describes properties about the injection of the template.
      """
      return [
        # "type" is the primary key, since by default each type uniquely maps to a specifically named template file
        {"type":"navbar","custom_bindings":False},
        {"type":"settings","custom_bindings":False},
      ]

    def get_assets(self):
      return dict(
        js=["js/helloworld.js"]
      )

__plugin__name__ = "Hello World"
__plugin_pythoncompat__ = ">=2.7,<4"
__plugin_implementation__ = HelloWorldPlugin()