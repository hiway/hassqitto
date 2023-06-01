import json
import time
from dataclasses import dataclass, field
from typing import Callable, Optional

import paho.mqtt.client as mqtt
from apscheduler.schedulers.background import BackgroundScheduler
from slugify import slugify

from .entity import Entity
from .logging import get_logger
from .topics import Topics


logger = get_logger(__name__)


@dataclass(kw_only=True)
class Device:
    """
    HomeAssistant MQTT Device
    """

    name: str
    name_slug: str = ""
    object_id: str = ""
    discovery_prefix: str = "homeassistant"
    component_type: str = "binary_sensor"
    entity_category: str = "diagnostic"

    configuration_url: str = ""
    connections: list[str] = field(default_factory=list)
    hw_version: str = ""
    identifiers: list[str] = field(default_factory=list)
    manufacturer: str = ""
    model: str = ""
    suggested_area: str = ""
    sw_version: str = ""
    via_device: str = ""

    client: Optional[mqtt.Client] = None
    entities: dict = field(default_factory=dict)
    base_topic: str = ""
    topics: Optional[Topics] = None
    scheduler: Optional[BackgroundScheduler] = None
    _on_connected_callback: Optional[Callable] = None

    def __post_init__(self):
        self.name_slug = slugify(self.name)
        if not self.object_id:
            self.object_id = self.name_slug
        self.client = mqtt.Client(client_id=self.object_id)
        if not self.identifiers:
            self.identifiers = [self.object_id]
        possible_entities = [
            getattr(self, name)
            for name in dir(self)
            if name not in self.__dict__ and not name.startswith("__")
        ]
        entities = [e for e in possible_entities if isinstance(e, Entity)]
        for entity in entities:
            assert entity.name not in self.entities
            entity.device = self
            self.entities.update({entity.name: entity})
        base_topic = f"{self.discovery_prefix}/{self.component_type}/{self.object_id}"
        self.topics = Topics(base_topic)
        self.scheduler = BackgroundScheduler()

    def connect(
        self,
        *,
        username: str,
        password: str,
        host: str = "homeassistant.local",
        port: int = 1883,
    ):
        assert self.client
        assert self.topics
        assert self.scheduler
        logger.debug("Connecting...")
        self.client.username_pw_set(username=username, password=password)
        self.client.connect(host=host, port=port)
        logger.debug("Connected.")
        self.client.loop_start()
        self.send_discovery()
        self.scheduler.start()
        if self._on_connected_callback:
            self._on_connected_callback()

    def disconnect(self):
        assert self.client
        assert self.scheduler
        assert self.topics
        logger.debug("Disconnecting...")
        self.scheduler.shutdown()
        self.client.loop_stop()
        self.client.disconnect()
        logger.debug("Disconnected.")

    def discovery_config(self):
        assert self.topics
        return {
            "name": "Online",
            "availability_topic": self.topics.availability,
            "payload_available": "online",
            "payload_not_available": "offline",
            "state_topic": self.topics.state,
            "object_id": self.object_id,
            "unique_id": self.object_id,
            "entity_category": self.entity_category,
            "device": self.device_info(),
        }

    def device_info(self):
        device_info = {
            "configuration_url": self.configuration_url,
            "connections": self.connections,
            "hw_version": self.hw_version,
            "identifiers": self.identifiers,
            "manufacturer": self.manufacturer,
            "model": self.model,
            "name": self.name,
            "suggested_area": self.suggested_area,
            "sw_version": self.sw_version,
            "via_device": self.via_device,
        }
        return {k: v for k, v in device_info.items() if v}

    def send_discovery(self):
        assert self.client
        assert self.topics
        self.client.publish(self.topics.config, json.dumps(self.discovery_config()))
        for entity in self.entities.values():
            time.sleep(0.2)
            logger.debug("Sending discovery for %s...", entity.name)
            entity.send_discovery()
            time.sleep(0.2)
            entity.set_available()

    def destroy_discovery(self):
        assert self.client
        assert self.topics
        for entity in self.entities.values():
            time.sleep(0.1)
            entity.destroy_discovery()
        self.client.publish(self.topics.config, "")
        logger.warning("Device %s discovery destroyed.", self.name)

    def publish_state(self, state):
        assert self.client
        assert self.topics
        self.client.publish(self.topics.state, state)
        logger.debug("Device %s published state: %s", self.name, state)

    def publish_availability(self, availability):
        assert self.client
        assert self.topics
        self.client.publish(self.topics.availability, availability)
        logger.debug("Device %s published availability: %s", self.name, availability)

    def set_available(self):
        self.publish_availability("online")
        logger.debug("Online.")

    def set_not_available(self):
        self.publish_availability("offline")
        logger.debug("Offline.")

    def set_online(self):
        self.publish_state("ON")
        logger.debug("State ON.")

    def set_offline(self):
        self.publish_state("OFF")
        logger.debug("State OFF.")

    def on_interval(
        self,
        seconds: Optional[int] = None,
        minutes: Optional[int] = None,
        hours: Optional[int] = None,
    ):
        """Run handler on interval"""

        def wrapper(func):
            assert self.scheduler
            kwargs = {"seconds": seconds, "minutes": minutes, "hours": hours}
            kwargs = {k: v for k, v in kwargs.items() if v}
            self.scheduler.add_job(func, "interval", **kwargs)
            return func

        return wrapper

    def on_connected(self, func):
        """Callback for connected event"""
        self._on_connected_callback = func
        return func

    def run(self):
        assert self.client
        self.client.loop_forever()
