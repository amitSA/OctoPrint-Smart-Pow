import asyncio
import time
from datetime import timedelta
from octoprint.events import EventManager
from octoprint_smart_pow.lib.event_manager_helpers import (
    fire_power_state_changed_event,
)
from octoprint_smart_pow.lib.smart_plug_client import SmartPlugClient
from octoprint_smart_pow.lib.data.power_state import (
    PowerState,
)
import logging
import kasa
from octoprint_smart_pow.lib.async_interval_scheduler import (
    AsyncIntervalScheduler,
)


class PowerStatePublisher:
    MAX_CONNECTION_FAILED_RETRY_ATTEMPTS = 20
    POLL_INTERVAL_FOR_READ = timedelta(seconds=2)

    """
    Listen to state change events for a a smart power plug, and broadcast them on the EventManager
    """

    def __init__(
        self,
        event_manager: EventManager,
        smart_plug: SmartPlugClient,
        logger=logging,
    ):
        self.logger = logger
        self.event_manager = event_manager
        self.smart_plug = smart_plug

        # An object that will call a routine on an interval
        self.interval_scheduler = AsyncIntervalScheduler(
            routine=self.__publish_if_changed,
            interval=self.POLL_INTERVAL_FOR_READ,
        )
        self.last_updated_state = PowerState.UNKNOWN

    def get_state(self) -> PowerState:
        return self.last_updated_state

    def start(self):
        """
        Start publishing events.
        """
        self.interval_scheduler.start()

    def stop(self):
        """
        Stop publishing events, and cleanup any resources like threads.
        """
        self.interval_scheduler.stop()

    async def __read_current_state(
        self,
        retry_attempts=MAX_CONNECTION_FAILED_RETRY_ATTEMPTS,
        backoff_seconds=5,
    ) -> PowerState:
        """
        Read the state power state, with retries
        """
        attempt = 1
        while True:
            try:
                return await self.smart_plug.read()
            except kasa.exceptions.SmartDeviceException as err:
                if attempt == retry_attempts:
                    raise
                self.logger.warning(
                    "Error when reading Smart Plug state, retry attempt %d/%d after backoff...",
                    attempt,
                    retry_attempts,
                )
                await asyncio.sleep(backoff_seconds)
            finally:
                attempt += 1

    async def __publish_if_changed(self):
        """
        Publishes a "power state changed" event if it has changed since the last time
        this method was called
        """
        current_state = await self.__read_current_state()

        if (
            self.last_updated_state != current_state
            or self.last_updated_state is None
        ):
            self.logger.info(
                "Publisher registered power state changed from %s to %s",
                self.last_updated_state,
                current_state,
            )
            fire_power_state_changed_event(self.event_manager, current_state)
            self.last_updated_state = current_state
