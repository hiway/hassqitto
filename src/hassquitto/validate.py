"""
Validation functions
"""
import re

from slugify import slugify


def name(name_: str) -> str:
    """
    Validate device or entity name.

    Args:
        name: Device name.

    Returns:
        Validated device name.

    Raises:
        ValueError: Invalid device name.
    """
    if not re.match(r"^[a-zA-Z0-9 ]+$", name_):
        raise ValueError("Invalid device name")
    return name_


def slug(name_: str) -> str:
    """
    Validate device or entity name and convert it to a slug.

    Args:
        name: Device name.

    Returns:
        Validated device slug.

    Raises:
        ValueError: Invalid device name
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
        ValueError: Invalid device name
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
