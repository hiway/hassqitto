from hassquitto import symbols


def test_binary_state_off():
    assert symbols.BinaryState.OFF.value == "OFF"


def test_binary_state_on():
    assert symbols.BinaryState.ON.value == "ON"
