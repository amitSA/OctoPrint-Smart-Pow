import funcy

class Events:
    prefix = None

    # TODO: encapsulate this logic into a decorator like this: @event(value="power_changed_event")
    @classmethod
    def POWER_STATE_CHANGED_EVENT_NAME(cls):
        return cls.__get_event_name(
            event="power_changed_event",
            prefix=cls.prefix
        )

    @classmethod
    def CONDITIONAL_POWER_OFF_ENABLED_EVENT_NAME(cls):
        return cls.__get_event_name(
            event="conditional_power_off_enabled_event",
            prefix=cls.prefix
        )

    @classmethod
    def set_prefix(cls,prefix):
        cls.prefix = prefix

    @classmethod
    def __get_event_name(cls, event,prefix=None):
        if prefix is not None:
            return f"{prefix}_{event}"
        return event
