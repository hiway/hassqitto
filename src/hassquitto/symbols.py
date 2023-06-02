from enum import Enum


class DeviceAvailability(Enum):
    OFFLINE = "offline"
    ONLINE = "online"


class SwitchState(Enum):
    OFF = "OFF"
    ON = "ON"
