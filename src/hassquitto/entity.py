import json
from dataclasses import dataclass
from typing import Callable, Optional, Any

from slugify import slugify

from .logging import get_logger
from .states import States
from .topics import Topics


logger = get_logger(__name__)


@dataclass(kw_only=True)
class Entity:
    """Entity"""

    name: str
    component_type: str
    name_slug: str = ""
    object_id: str = ""
    discovery_prefix: str = "homeassistant"

    device_class: Optional[str] = None
    entity_category: Optional[str] = None

    topics: Optional[Topics] = None
    device: Optional[Any] = None  # type: ignore
    command_handler: Optional[Callable] = None
    initial_state: Optional[Any] = None

    def __post_init__(self):
        self.name_slug = slugify(self.name)

    def on_command(self, func):
        def _wrapper(_client, _userdata, message):
            func(message.payload.decode())

        self.command_handler = _wrapper
        return func

    def send_discovery(self):
        assert self.device
        assert self.device.client
        if not self.object_id:
            self.object_id = self.device.object_id + "_" + self.name_slug
        base_topic = f"{self.discovery_prefix}/{self.component_type}/{self.object_id}"
        self.topics = Topics(base_topic)
        if self.command_handler:
            self.device.client.message_callback_add(
                self.topics.command, self.command_handler
            )
            self.device.client.subscribe(self.topics.command)
        self.device.client.publish(
            self.topics.config, json.dumps(self.discovery_config())
        )
        if self.initial_state:
            self.publish_state(self.initial_state)

    def destroy_discovery(self):
        assert self.device
        assert self.device.client
        assert self.topics
        self.device.client.publish(self.topics.config, "")

    def discovery_config(self):
        assert self.device
        assert self.topics
        device_config = self.device.discovery_config()
        device_config["name"] = self.name
        device_config["object_id"] = self.object_id
        device_config["unique_id"] = self.object_id
        device_config["availability_topic"] = self.topics.availability
        device_config["state_topic"] = self.topics.state
        device_config["command_topic"] = self.topics.command
        if self.entity_category:
            device_config["entity_category"] = self.entity_category
        else:
            del device_config["entity_category"]
        if self.device_class:
            device_config["device_class"] = self.device_class
        if (
            isinstance(self, Sensor) and self.unit_of_measurement
        ):  # pylint: disable = no-member
            device_config[
                "unit_of_measurement"
            ] = self.unit_of_measurement  # pylint: disable = no-member
        return device_config

    def set_available(self):
        assert self.device
        assert self.device.client
        assert self.topics
        self.device.client.publish(self.topics.availability, "online")
        logger.debug("%s is Online.", self.name)

    def set_unavailable(self):
        assert self.device
        assert self.device.client
        assert self.topics
        self.device.client.publish(self.topics.availability, "offline")
        logger.debug("%s is Offline.", self.name)

    def publish_state(self, state):
        assert self.device
        assert self.device.client
        assert self.topics
        if isinstance(state, States):
            state = state.value
        if isinstance(state, dict):
            state = json.dumps(state)
        self.device.client.publish(self.topics.state, state)
        logger.debug("Entity %s published state: %s", self.name, state)


@dataclass(kw_only=True)
class AlarmControlPanel(Entity):
    """Alarm Control Panel Entity"""

    component_type: str = "alarm_control_panel"


@dataclass(kw_only=True)
class BinarySensor(Entity):
    """Binary Sensor Entity"""

    component_type: str = "binary_sensor"


@dataclass(kw_only=True)
class Button(Entity):
    """Button Entity"""

    component_type: str = "button"


@dataclass(kw_only=True)
class Camera(Entity):
    """Camera Entity"""

    component_type: str = "camera"


@dataclass(kw_only=True)
class Cover(Entity):
    """Cover Entity"""

    component_type: str = "cover"


@dataclass(kw_only=True)
class DeviceTracker(Entity):
    """Device Tracker Entity"""

    component_type: str = "device_tracker"


@dataclass(kw_only=True)
class DeviceTrigger(Entity):
    """Device Trigger Entity"""

    component_type: str = "device_trigger"


@dataclass(kw_only=True)
class Fan(Entity):
    """Fan Entity"""

    component_type: str = "fan"


@dataclass(kw_only=True)
class Humidifier(Entity):
    """Humidifier Entity"""

    component_type: str = "humidifier"


@dataclass(kw_only=True)
class Climate(Entity):
    """Climate Entity"""

    component_type: str = "climate"


@dataclass(kw_only=True)
class Light(Entity):
    """Light Entity"""

    component_type: str = "light"


@dataclass(kw_only=True)
class Lock(Entity):
    """Lock Entity"""

    component_type: str = "lock"


@dataclass(kw_only=True)
class Number(Entity):
    """Number Entity"""

    component_type: str = "number"


@dataclass(kw_only=True)
class Scene(Entity):
    """Scene Entity"""

    component_type: str = "scene"


@dataclass(kw_only=True)
class Select(Entity):
    """Select Entity"""

    component_type: str = "select"


@dataclass(kw_only=True)
class Sensor(Entity):
    """Sensor Entity"""

    component_type: str = "sensor"
    unit_of_measurement: Optional[str] = None


@dataclass(kw_only=True)
class Siren(Entity):
    """Siren Entity"""

    component_type: str = "siren"


@dataclass(kw_only=True)
class Switch(Entity):
    """Switch Entity"""

    component_type: str = "switch"


@dataclass(kw_only=True)
class Update(Entity):
    """Update Entity"""

    component_type: str = "update"


@dataclass(kw_only=True)
class TagScanner(Entity):
    """Tag Scanner Entity"""

    component_type: str = "tag_scanner"


@dataclass(kw_only=True)
class Text(Entity):
    """Text Entity"""

    component_type: str = "text"


@dataclass(kw_only=True)
class Vacuum(Entity):
    """Vacuum Entity"""

    component_type: str = "vacuum"
