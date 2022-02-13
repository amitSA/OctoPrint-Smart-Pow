import funcy


class Events:
    prefix = None

    # TODO: encapsulate this logic into a decorator like this: @event(value="power_changed_event")
    @classmethod
    def POWER_STATE_CHANGED_EVENT(cls):
        return cls.__get_event_name(
            event="power_state_changed_event", prefix=cls.prefix
        )

    @classmethod
    def POWER_STATE_DO_CHANGE_EVENT(cls):
        return cls.__get_event_name(
            event="power_state_do_change_event", prefix=cls.prefix
        )

    # TODO: this should be renamed to something to do with "scheduling"
    # Its confusing what this means right now
    @classmethod
    def AUTOMATIC_POWER_OFF_CHANGED_EVENT(cls):
        return cls.__get_event_name(
            event="conditional_power_off_changed_event", prefix=cls.prefix
        )

    @classmethod
    def AUTOMATIC_POWER_OFF_DO_CHANGE_EVENT(cls):
        return cls.__get_event_name(
            event="conditional_power_off_do_change_event", prefix=cls.prefix
        )

    @classmethod
    def set_prefix(cls, prefix):
        cls.prefix = prefix

    @classmethod
    def __get_event_name(cls, event, prefix=None):
        if prefix is not None:
            return f"{prefix}_{event}"
        return event
