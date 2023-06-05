import asyncio
import functools
import logging
import json
import time
import threading
from dataclasses import dataclass, field
from inspect import isawaitable, iscoroutinefunction
from typing import Callable, Coroutine, Optional, Union

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from asyncgnostic import awaitable

from hassquitto import symbols, validate
from hassquitto.logging import get_logger
from hassquitto.topics import Topics
from hassquitto.transport import MqttTransport


logger = get_logger("custom.device")
logger.setLevel(logging.DEBUG)
logging.getLogger("hassquitto").setLevel(logging.DEBUG)


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
        self.via_device = self.via_device
        self.configuration_url = validate.url(self.configuration_url)
        self.discovery_prefix = validate.discovery_prefix(self.discovery_prefix)
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
        self._status = None  # type: Optional[str]
        self._available = False

        self._mqtt = MqttTransport(client_id=validate.slug(self.name))

        self._scheduler: AsyncIOScheduler = None
        self._scheduled_jobs = {}
        self._loop: asyncio.AbstractEventLoop = None
        self._thread: Optional[threading.Thread] = None

        self._start_event = asyncio.Event()
        self._stop_event = asyncio.Event()
        self._connected_event = asyncio.Event()
        self._available_event = asyncio.Event()
        self._status_was_set_event = asyncio.Event()

        self._on_connect: Optional[Union[Callable, Coroutine]] = None
        self._on_disconnect: Optional[Union[Callable, Coroutine]] = None
        self._on_message: Optional[Union[Callable, Coroutine]] = None

    def __repr__(self):
        return f"<Device name={self.name}>"

    def sleep(self, seconds: float):  # type: ignore
        logger.debug("sleep(%s)", seconds)
        time.sleep(seconds)

    @awaitable(sleep)
    async def sleep(self, seconds: float):
        logger.debug("sleep(%s)", seconds)
        await asyncio.sleep(seconds)

    def on_interval(self, interval: int):
        def decorator(func):
            logger.debug("on_interval decorator called with func: %s", func)
            if iscoroutinefunction(func) or isawaitable(func):
                logger.debug("on_interval decorator is ASYNC")
                # self._scheduler.add_job(func, "interval", seconds=interval)
                self._scheduled_jobs[func] = interval
            else:
                logger.debug("on_interval decorator is SYNC")

                @functools.wraps(func)
                async def wrapper():
                    try:
                        return self._loop.run_in_executor(None, func)
                    except Exception as error:
                        logger.exception(error)

                # self._scheduler.add_job(wrapper, "interval", seconds=interval)
                self._scheduled_jobs[wrapper] = interval
            return func

        return decorator

    def connect(
        self,
        *,
        username: str,
        password: str,
        host: str = "homeassistant.local",
        port: int = 1883,
    ):
        self._mqtt.on_connect(self._on_connect_callback)
        self._mqtt.on_disconnect(self._on_disconnect_callback)
        self._mqtt.on_message(self._on_message_callback)
        self._mqtt.connect(
            username=username,
            password=password,
            host=host,
            port=port,
        )
        logger.debug("Waiting for connected event")
        while not self._connected_event.is_set():
            time.sleep(0.1)
        logger.debug("Connected")
        while not self._available_event.is_set():
            time.sleep(0.1)
        logger.debug("Available")
        if not self._on_connect:
            logger.debug("No on_connect function defined")
            return
        if callable(self._on_connect):
            logger.debug("Calling on_connect function")
            self._on_connect()
        elif iscoroutinefunction(self._on_connect):
            logger.debug("Calling on_connect coroutine")
            self._loop.create_task(self._on_connect())

    @awaitable(connect)
    async def connect(
        self,
        *,
        username: str,
        password: str,
        host: str = "homeassistant.local",
        port: int = 1883,
    ):
        self._mqtt.on_connect(self._on_connect_callback_async)
        self._mqtt.on_disconnect(self._on_disconnect_callback_async)
        self._mqtt.on_message(self._on_message_callback_async)
        await self._mqtt.connect(
            username=username,
            password=password,
            host=host,
            port=port,
        )
        logger.debug("Waiting for connected event")
        await self._connected_event.wait()
        logger.debug("Connected")
        await self._available_event.wait()
        logger.debug("Available")

        if not self._on_connect:
            logger.debug("No on_connect function defined")
            return
        if iscoroutinefunction(self._on_connect):
            logger.debug("Calling on_connect coroutine")
            await self._on_connect()
        elif callable(self._on_connect):
            logger.debug("Calling on_connect function")
            self._loop.create_task(self._on_connect())

    def disconnect(self):
        logger.debug("disconnect()")
        self._mqtt.disconnect()

    @awaitable(disconnect)
    async def disconnect(self):
        logger.debug("disconnect()")
        await self._mqtt.disconnect()

    @property
    def _device_config(self):
        config = {
            "name": validate.name(self.name),
            "manufacturer": validate.name(self.manufacturer, allow_empty=True),
            "model": validate.name(self.model, allow_empty=True),
            "sw_version": validate.version_string(self.sw_version),
            "hw_version": validate.version_string(self.hw_version),
            "via_device": self.via_device,
            "configuration_url": validate.url(self.configuration_url),
            "suggested_area": self.suggested_area,
            "identifiers": self.identifiers,
            "connections": self.connections,
        }
        return {k: v for k, v in config.items() if v}

    @property
    def _status_config(self):
        config = {
            "name": "Status",
            "availability_topic": self._topics.availability,
            "payload_available": symbols.DeviceAvailability.ONLINE.value,
            "payload_not_available": symbols.DeviceAvailability.OFFLINE.value,
            "state_topic": self._topics.state,
            "object_id": self._object_id,
            "unique_id": self._unique_id,
            "entity_category": self._entity_category,
            "icon": "mdi:information-outline",
            "device": self._device_config,
        }
        return config

    def _on_connect_callback(self, client, userdata, flags, rc):
        logger.debug("on_connect_callback called with rc=%s", rc)
        self._mqtt.subscribe(self._topics.command)
        self._mqtt.subscribe(self._topics.state)
        self._mqtt.subscribe(self._topics.availability)
        self._mqtt.subscribe(self._topics.config)
        self._mqtt.publish(self._topics.config, json.dumps(self._status_config))
        time.sleep(0.5)
        self._connected_event.set()

    async def _on_connect_callback_async(self, client, userdata, flags, rc):
        logger.debug("on_connect_callback_async called with rc=%s", rc)
        await self._mqtt.subscribe(self._topics.command)
        await self._mqtt.subscribe(self._topics.state)
        await self._mqtt.subscribe(self._topics.availability)
        await self._mqtt.subscribe(self._topics.config)
        await self._mqtt.publish(self._topics.config, json.dumps(self._status_config))
        await asyncio.sleep(0.5)
        self._connected_event.set()

    def _on_disconnect_callback(self, client, userdata, rc):
        logger.debug("on_disconnect_callback called with rc=%s", rc)
        if not self._on_disconnect:
            return
        if callable(self._on_disconnect):
            logger.debug("Calling on_disconnect function")
            self._on_disconnect()
        elif iscoroutinefunction(self._on_disconnect):
            logger.debug("Calling on_disconnect coroutine")
            self._loop.create_task(self._on_disconnect())

    async def _on_disconnect_callback_async(self, client, userdata, rc):
        logger.debug("on_disconnect_callback_async called with rc=%s", rc)
        if not self._on_disconnect:
            return
        if iscoroutinefunction(self._on_disconnect):
            logger.debug("Calling on_disconnect coroutine")
            await self._on_disconnect()
        elif callable(self._on_disconnect):
            logger.debug("Calling on_disconnect function")
            self._on_disconnect()

    def _on_message_callback(self, client, userdata, message):
        logger.debug(
            "on_message_callback called with topic: %s, message: %s",
            message.topic,
            message.payload,
        )
        if self._process_internal_messages(message):
            return
        if not self._on_message:
            return
        if callable(self._on_message):
            logger.debug("Calling on_message function")
            self._on_message(message)
        elif iscoroutinefunction(self._on_message):
            logger.debug("Calling on_message coroutine")
            self._loop.create_task(self._on_message(message))

    async def _on_message_callback_async(self, client, userdata, message):
        logger.debug(
            "on_message_callback called with topic: %s, message: %s",
            message.topic,
            message.payload,
        )
        if self._process_internal_messages(message):
            return
        if not self._on_message:
            return
        if iscoroutinefunction(self._on_message):
            logger.debug("Calling on_message coroutine")
            await self._on_message(message)
        elif callable(self._on_message):
            logger.debug("Calling on_message function")
            self._on_message(message)

    def _process_internal_messages(self, message):
        if message.topic == self._topics.config and message.payload != b"":
            logger.debug("Received config message, setting availability to online")
            time.sleep(0.1)
            self.available()
            return True
        if message.topic == self._topics.availability and message.payload == b"online":
            if self._available:
                return True
            self._available_event.set()
            self._available = True
            return True
        if message.topic == self._topics.state:
            self._status = message.payload.decode()
            self._status_was_set_event.set()
            return True
        return False

    def on_connect(self, func):
        logger.debug("on_connect called with func: %s", func)
        self._on_connect = func

    def on_disconnect(self, func):
        logger.debug("on_disconnect called with func: %s", func)
        self._on_disconnect = func

    def on_message(self, func):
        logger.debug("on_message called with func: %s", func)
        self._on_message = func

    def available(self):
        logger.debug("available called")
        self._mqtt.publish(self._topics.availability, "online")

    @awaitable(available)
    async def available(self):
        logger.debug("available called")
        await self._mqtt.publish(self._topics.availability, "online")

    def not_available(self):
        logger.debug("not_available called")
        self._mqtt.publish(self._topics.availability, "offline")

    @awaitable(not_available)
    async def not_available(self):
        logger.debug("not_available called")
        await self._mqtt.publish(self._topics.availability, "offline")

    def status(self, status: str):
        logger.debug("status called with status: %s", status)
        self._mqtt.publish(self._topics.state, status)

    @awaitable(status)
    async def status(self, status: str):
        logger.debug("status called with status: %s", status)
        await self._mqtt.publish(self._topics.state, status)

    def status_set_confirm(self):
        logger.debug("status_set_confirm called")
        while not self._status_was_set_event.is_set():
            time.sleep(0.1)
        self._status_was_set_event.clear()

    @awaitable(status_set_confirm)
    async def status_set_confirm(self):
        logger.debug("status_set_confirm called")
        while not self._status_was_set_event.is_set():
            await asyncio.sleep(0.1)
        self._status_was_set_event.clear()

    def destroy(self):
        logger.debug("destroy called")
        self._mqtt.publish(self._topics.config, "")

    @awaitable(destroy)
    async def destroy(self):
        logger.debug("destroy called")
        await self._mqtt.publish(self._topics.config, "")

    def start(self, loop_forever: bool = False):  # type: ignore
        logger.debug("=== SYNC start()")
        loop_forever = True
        self._thread = threading.Thread(
            target=asyncio.run,
            daemon=True,
            args=(self._start(loop_forever=loop_forever),),
        )
        self._thread.start()
        while not self._start_event.is_set():
            time.sleep(0.1)

    @awaitable(start)
    async def start(self, loop_forever: bool = False):
        logger.debug("~~~ ASYNC start()")
        await self._start(loop_forever=loop_forever)
        await self._start_event.wait()

    async def _start(self, loop_forever: bool = False):
        logger.debug("Starting device")
        self._loop = asyncio.get_event_loop()

        logger.debug("Starting scheduler")
        self._scheduler = AsyncIOScheduler(event_loop=self._loop)
        self._scheduler.add_job(lambda: True, "interval", seconds=0.2)
        for job, interval in self._scheduled_jobs.items():
            logger.debug("Creating scheduled job %s for interval: %s", job, interval)
            self._scheduler.add_job(job, "interval", seconds=interval)
        self._scheduler.start()
        self._start_event.set()

        if loop_forever:
            await self._stop_event.wait()

    def run(self):  # type: ignore
        logger.debug("=== SYNC run()")
        self.start(loop_forever=True)  # type: ignore
        if self._thread:
            self._thread.join()

    @awaitable(run)
    async def run(self):
        logger.debug("~~~ ASYNC run()")
        await self.start(loop_forever=True)

    def stop(self):  # type: ignore
        logger.debug("=== SYNC stop()")
        task = self._loop.create_task(self._stop())
        if self._thread:
            logger.debug("Waiting for thread to join")
            self._thread.join()

    @awaitable(stop)
    async def stop(self):
        logger.debug("~~~ ASYNC stop()")
        await self._stop()

    async def _stop(self):
        logger.debug("Stopping device")
        logger.debug("Stopping scheduler")
        self._scheduler.shutdown()
        await self._mqtt.disconnect()
        self._stop_event.set()
