from hassquitto import symbols


def test_device_availability():
    assert symbols.DeviceAvailability.OFFLINE.value == "offline"
    assert symbols.DeviceAvailability.ONLINE.value == "online"


def test_switch_state():
    assert symbols.SwitchState.OFF.value == "OFF"
    assert symbols.SwitchState.ON.value == "ON"


def test_entity_category():
    assert symbols.EntityCategory.DIAGNOSTIC.value == "diagnostic"
    assert symbols.EntityCategory.CONFIG.value == "config"


def test_mqtt_qos():
    assert symbols.MqttQos.AT_MOST_ONCE.value == 0
    assert symbols.MqttQos.AT_LEAST_ONCE.value == 1
    assert symbols.MqttQos.EXACTLY_ONCE.value == 2
