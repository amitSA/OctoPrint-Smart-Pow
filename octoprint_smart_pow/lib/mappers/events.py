# def qualify_event_name(event, plugin_name=None):
#     """
#     When we register custom events with Octoprint, Octoprint actually
#     transforms the names to namespace them from other events

#     See this documentation on the transformation
#     https://docs.octoprint.org/en/master/plugins/hooks.html#octoprint-events-register-custom-events
#     """
#     return __quality_event_name(
#         event=event,
#         plugin_name=(plugin_name if not None else __parse_plugin_name())
#     )


# def __quality_event_name(event,plugin_name):
#     return f"plugin_{plugin_name}_{event}"

# def __parse_plugin_name():
#     pass
