"""
Device
"""
import asyncio
import json
import signal
import time
import threading
from dataclasses import dataclass, field
from inspect import isawaitable, iscoroutinefunction
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from asgiref.sync import async_to_sync
from asyncgnostic import awaited, awaitable

from . import symbols, validate
from .logging import get_logger
from .topics import Topics
from .transport import AsyncMQTT


logger = get_logger(__name__)


@dataclass(kw_only=True)
class Device:
    name: str
    manufacturer: str = ""
    model: str = ""
    sw_version: str = ""
    hw_version: str = ""
    identifiers: list[str] = field(default_factory=list)
    connections: list[str] = field(default_factory=list)
    via_device: str = ""
    configuration_url: str = ""
    discovery_prefix: str = "homeassistant"
    suggested_area: str = ""

    def __post_init__(self):
        self.name = validate.name(self.name)
        self.manufacturer = validate.name(self.manufacturer, allow_empty=True)
        self.model = validate.name(self.model, allow_empty=True)
        self.sw_version = validate.version_string(self.sw_version)
        self.hw_version = validate.version_string(self.hw_version)
        self.via_device = validate.slug(self.via_device)
        self.configuration_url = validate.url(self.configuration_url)
        self.discovery_prefix = validate.discovery_prefix(self.discovery_prefix)

        self._mqtt = AsyncMQTT(client_id=self.name)
        self._scheduler = AsyncIOScheduler()
        self._name_slug = validate.slug(self.name)
        self._object_id = validate.object_id(self.name)
        self._unique_id = validate.unique_id(self.name)
        self._entity_category = "diagnostic"
        self._component_type = "sensor"
        self._topics = Topics(
            base=f"{self.discovery_prefix}/{self._component_type}/{self._object_id}"
        )
        if not self.identifiers:
            self.identifiers = [self._object_id]

        self._status = None
        self._on_connect_callback = None
        self._queue = asyncio.Queue()

    async def start(
        self,
        host: str = "homeassistant.local",
        port: int = 1883,
        username: str = None,
        password: str = None,
        loop_forever: bool = True,
    ):
        self._mqtt.loop = asyncio.get_event_loop()
        self._mqtt.on_connect(self._start)
        self._mqtt.on_message(self._on_message)
        logger.info("Connecting to MQTT broker")
        await self._mqtt.connect(
            host=host,
            port=port,
            username=username,
            password=password,
        )
        try:
            while loop_forever:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass

    def run(
        self,
        host: str = "homeassistant.local",
        port: int = 1883,
        username: str = None,
        password: str = None,
    ):
        if awaited():
            return self.start(
                host=host,
                port=port,
                username=username,
                password=password,
                loop_forever=False,
            )
        else:
            threading.Thread(
                target=asyncio.run,
                args=(
                    self.start(
                        host=host,
                        port=port,
                        username=username,
                        password=password,
                        loop_forever=True,
                    ),
                ),
                daemon=True,
            ).start()
            while self._queue.empty():
                time.sleep(0.1)

    def destroy(self):
        logger.info("Removing device from Home Assistant")
        return self._mqtt.publish(self._topics.config, "")

    @awaitable(destroy)
    async def destroy(self):
        logger.info("Removing device from Home Assistant")
        await self._mqtt.publish(self._topics.config, "")

    def stop(self, loop: Optional[asyncio.AbstractEventLoop] = None):
        logger.info("Disconnecting from MQTT broker")
        if loop is None:
            return self._mqtt.disconnect()
        else:
            # Gather all pending tasks
            tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]

            # Cancel all pending tasks
            for task in tasks:
                task.cancel()

            # Wait for all pending tasks to be cancelled
            cancel_task = loop.create_task(asyncio.gather(*tasks, return_exceptions=True))
            while True:
                if cancel_task.done():
                    break
                time.sleep(0.1)
            loop.stop()



    @awaitable(stop)
    async def stop(self, loop: Optional[asyncio.AbstractEventLoop] = None):
        logger.info("Disconnecting from MQTT broker")
        await self._mqtt.disconnect()

    @property
    def _device_config(self):
        config = {
            "name": self.name,
            "manufacturer": self.manufacturer,
            "model": self.model,
            "sw_version": self.sw_version,
            "hw_version": self.hw_version,
            "identifiers": self.identifiers,
            "connections": self.connections,
            "via_device": self.via_device,
            "configuration_url": self.configuration_url,
            "suggested_area": self.suggested_area,
        }
        return {k: v for k, v in config.items() if v}

    async def _start(self, client, userdata, flags, rc):
        if rc != 0:
            logger.error(f"Connection failed with code {rc}")
            return
        config = {
            "name": "Status",
            "availability_topic": self._topics.availability,
            "payload_available": symbols.DeviceAvailability.ONLINE.value,
            "payload_not_available": symbols.DeviceAvailability.OFFLINE.value,
            "state_topic": self._topics.state,
            "object_id": self._object_id,
            "unique_id": self._unique_id,
            "entity_category": self._entity_category,
            "device": self._device_config,
            "icon": "mdi:information-outline",
        }
        logger.info("Publishing device config")
        config_topic = self._topics.config
        await self._mqtt.publish(config_topic, json.dumps(config))
        await self._mqtt.subscribe(self._topics.command)
        await self._mqtt.subscribe(self._topics.state)
        await asyncio.sleep(1)
        await self.available()
        self._scheduler.start()
        if self._on_connect_callback:
            logger.info("Running on_connect callback")
            if iscoroutinefunction(self._on_connect_callback):
                await self._on_connect_callback()
            else:
                self._on_connect_callback()
        await self._queue.put(True)

    async def _on_message(self, client, userdata, message):
        if message.topic == self._topics.command:
            await self._on_command(message.payload.decode())
        elif message.topic == self._topics.state:
            await self._on_state(message.payload.decode())

    async def _on_command(self, payload):
        logger.info(f"Received command: {payload}")

    async def _on_state(self, payload):
        logger.info(f"Received state: {payload}")
        self._status = payload.decode()

    def available(self):
        logger.info("Device is available")
        return self._mqtt.publish(
            self._topics.availability,
            symbols.DeviceAvailability.ONLINE.value,
        )

    @awaitable(available)
    async def available(self):
        logger.info("Device is available")
        await self._mqtt.publish(
            self._topics.availability,
            symbols.DeviceAvailability.ONLINE.value,
        )

    def unavailable(self):
        logger.info("Device is unavailable")
        return self._mqtt.publish(
            self._topics.availability,
            symbols.DeviceAvailability.OFFLINE.value,
        )

    @awaitable(unavailable)
    async def unavailable(self):
        logger.info("Device is unavailable")
        await self._mqtt.publish(
            self._topics.availability,
            symbols.DeviceAvailability.OFFLINE.value,
        )

    def status(self, status: Optional[str] = None, retain: bool = False):
        if status is None:
            logger.info(f"Get device status: {self._status}")
            return self._status
        self._mqtt.publish(self._topics.state, status, retain=retain)
        self._status = status
        logger.info(f"Publish device status: {status}")

    @awaitable(status)
    async def status(self, status: Optional[str] = None, retain: bool = False):
        if status is None:
            logger.info(f"Get device status: {self._status}")
            return self._status
        await self._mqtt.publish(self._topics.state, status, retain=retain)
        self._status = status
        logger.info(f"Publish device status: {status}")

    def on_connect(self, func):
        self._on_connect_callback = func
        return func

    def on_interval(
        self,
        seconds: Optional[int] = None,
        minutes: Optional[int] = None,
        hours: Optional[int] = None,
    ):
        def decorator(func):
            kwargs = {"seconds": seconds, "minutes": minutes, "hours": hours}
            kwargs = {k: v for k, v in kwargs.items() if v}
            self.scheduler.add_job(func, "interval", **kwargs)
            return func

        return decorator

    def sleep(self, seconds: float):
        return async_to_sync(asyncio.sleep)(seconds)

    @awaitable(sleep)
    async def sleep(self, seconds: float):
        return await asyncio.sleep(seconds)
