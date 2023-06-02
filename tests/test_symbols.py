from hassquitto import symbols


def test_device_availability_offline():
    assert symbols.DeviceAvailability.OFFLINE.value == "offline"


def test_device_availability_online():
    assert symbols.DeviceAvailability.ONLINE.value == "online"


def test_switch_state_off():
    assert symbols.SwitchState.OFF.value == "OFF"


def test_switch_state_on():
    assert symbols.SwitchState.ON.value == "ON"
