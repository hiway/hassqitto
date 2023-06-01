from dataclasses import dataclass


@dataclass
class Topics:
    """
    Entity MQTT Topics

    Args:
        base: Base topic.
        availability (optional): Availability topic.
        config (optional): Config topic.
        command (optional): Command topic.
        state (optional): State topic.
    """

    base: str
    availability: str = ""
    config: str = ""
    command: str = ""
    state: str = ""

    def __post_init__(self):
        self.availability = self.availability or f"{self.base}/availability"
        self.config = self.config or f"{self.base}/config"
        self.command = self.command or f"{self.base}/command"
        self.state = self.state or f"{self.base}/state"
