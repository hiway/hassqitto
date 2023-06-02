import pytest
from hassquitto import validate


def test_name_valid():
    assert validate.name("Valid Name 123") == "Valid Name 123"


def test_name_invalid():
    with pytest.raises(ValueError):
        validate.name("Invalid Name @#$")


def test_slug_valid():
    assert validate.slug("Valid Name 123") == "valid-name-123"


def test_slug_invalid():
    with pytest.raises(ValueError):
        validate.slug("Invalid Name @#$")


def test_object_id_valid():
    assert validate.object_id("Valid Name 123") == "valid_name_123"


def test_object_id_invalid():
    with pytest.raises(ValueError):
        validate.object_id("Invalid Name @#$")


def test_unique_id_valid():
    assert validate.unique_id("Valid Name 123") == "valid_name_123"


def test_unique_id_invalid():
    with pytest.raises(ValueError):
        validate.unique_id("Invalid Name @#$")


def test_discovery_prefix_valid():
    assert validate.discovery_prefix("homeassistant") == "homeassistant"
    assert validate.discovery_prefix("valid_prefix_123") == "valid_prefix_123"


def test_discovery_prefix_invalid():
    with pytest.raises(ValueError):
        validate.discovery_prefix("invalid_prefix @#$")


def test_component_type_valid():
    assert validate.component_type("valid_type_123") == "valid_type_123"


def test_component_type_invalid():
    with pytest.raises(ValueError):
        validate.component_type("invalid_type @#$")


def test_topic_valid():
    assert (
        validate.topic("homeassistant/switch/transport_test/state")
        == "homeassistant/switch/transport_test/state"
    )


def test_topic_invalid():
    with pytest.raises(ValueError):
        validate.topic("homeassistant-switch-transport_test-state")
