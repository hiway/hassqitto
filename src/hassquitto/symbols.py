from enum import Enum


class DeviceAvailability(Enum):
    OFFLINE = "offline"
    ONLINE = "online"


class SwitchState(Enum):
    OFF = "OFF"
    ON = "ON"


class EntityCategory(Enum):
    DIAGNOSTIC = "diagnostic"
    CONFIG = "config"


class MqttQos(Enum):
    AT_MOST_ONCE = 0
    AT_LEAST_ONCE = 1
    EXACTLY_ONCE = 2
