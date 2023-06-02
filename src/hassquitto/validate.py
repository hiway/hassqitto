"""
Validation functions
"""
import re
from urllib.parse import urlparse

from slugify import slugify as _slugify


def name(name_: str, allow_empty: bool = False) -> str:
    """
    Validate device or entity name.

    Args:
        name: Device or entity name.

    Returns:
        Validated name.

    Raises:
        ValueError: Invalid name.
    """
    if allow_empty and not name_:
        return name_
    if not re.match(r"^[a-zA-Z0-9 ]+$", name_):
        raise ValueError(f"Invalid name: {name_!r}")
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
    if not name_:
        return name_
    return _slugify(name(name_))


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
    if not re.match(r"^[a-zA-Z0-9_ ]+$", name_):
        raise ValueError("Invalid object ID")
    return _slugify(name_).replace("-", "_")


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
    if not re.match(r"^[a-zA-Z0-9_ ]+$", name_):
        raise ValueError("Invalid unique ID")
    return _slugify(name_).replace("-", "_")


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


def version_string(version_string_: str) -> str:
    """
    Validate version string.

    Args:
        name: Version string.

    Returns:
        Validated version string.

    Raises:
        ValueError: Invalid version string.
    """
    if not version_string_:
        return version_string_
    if not re.match(r"^[a-zA-Z0-9_.-]+$", version_string_):
        raise ValueError("Invalid version string")
    return version_string_


def url(url_: str) -> str:
    """
    Validate URL.

    Args:
        name: URL.

    Returns:
        Validated URL.

    Raises:
        ValueError: Invalid URL.
    """
    if not url_:
        return url_
    try:
        result = urlparse(url_)
        if not all([result.scheme, result.netloc]):
            raise ValueError("Invalid URL")
    except ValueError:
        raise ValueError("Invalid URL")
    return url_
