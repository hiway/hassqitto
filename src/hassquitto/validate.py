"""
Validation functions
"""
import re

from slugify import slugify


def name(name_: str) -> str:
    """
    Validate device or entity name.

    Args:
        name: Device or entity name.

    Returns:
        Validated name.

    Raises:
        ValueError: Invalid name.
    """
    if not re.match(r"^[a-zA-Z0-9 ]+$", name_):
        raise ValueError("Invalid name")
    return name_


def slug(name_: str) -> str:
    """
    Validate device or entity name and convert it to a slug.

    Args:
        name: Device name.

    Returns:
        Validated device slug.

    Raises:
        ValueError: Invalid name
    """
    return slugify(name(name_))


def object_id(name_: str) -> str:
    """
    Validate device or entity name and convert it to a Home Assistant object ID.

    Args:
        name: Device name.

    Returns:
        Validated device object ID.

    Raises:
        ValueError: Invalid name
    """
    return slug(name_).replace("-", "_")


def unique_id(name_: str) -> str:
    """
    Validate device or entity name and convert it to a Home Assistant unique ID.

    Args:
        name: Device name.

    Returns:
        Validated device unique ID.

    Raises:
        ValueError: Invalid name
    """
    return slug(name_).replace("-", "_")


def discovery_prefix(discovery_prefix_: str) -> str:
    """
    Validate discovery prefix.

    Args:
        name: Discovery prefix.

    Returns:
        Validated discovery prefix.

    Raises:
        ValueError: Invalid discovery prefix.
    """
    if not re.match(r"^[a-zA-Z0-9_]+$", discovery_prefix_):
        raise ValueError("Invalid discovery prefix")
    return discovery_prefix_


def component_type(component_type_: str) -> str:
    """
    Validate component type.

    Args:
        name: Component type.

    Returns:
        Validated component type.

    Raises:
        ValueError: Invalid component type.
    """
    if not re.match(r"^[a-zA-Z0-9_]+$", component_type_):
        raise ValueError("Invalid component type")
    return component_type_


def topic(topic_: str) -> str:
    """
    Validate topic.

    Args:
        name: Topic.

    Returns:
        Validated topic.

    Raises:
        ValueError: Invalid topic.
    """
    if not re.match(r"^[a-zA-Z0-9_/]+$", topic_):
        raise ValueError("Invalid topic")
    return topic_
