import asyncio
import logging
import json

from hassquitto.logging import get_logger
from hassquitto.symbols import DeviceAvailability, SwitchState
from hassquitto.transport import MqttTransport

# Setup logging
logger = get_logger(__name__)
logger.setLevel(logging.DEBUG)
logging.getLogger("hassquitto").setLevel(logging.DEBUG)

# Instantiate MQTT transport
transport = MqttTransport(client_id="transport-test")


# Define callback for MQTT connection
@transport.on_connect
async def on_connect(client, userdata, flags, rc):
    logger.info("Connected with result code %s", rc)


# Define callback for MQTT message
@transport.on_message
async def on_message(client, userdata, msg):
    logger.info("Received message on topic %s: %s", msg.topic, msg.payload.decode())


# Define callback for MQTT disconnection
@transport.on_disconnect
async def on_disconnect(client, userdata, rc):
    logger.info("Disconnected with result code %s", rc)


async def main():
    # Connect to MQTT broker
    await transport.connect(
        host="homeassistant.local",
        port=1883,
        username="example",
        password="example",
    )
    # Wait for connection to be established
    await asyncio.sleep(1)

    # Configure switch entity
    message = json.dumps(
        {
            "name": "Transport Test Switch",
            "availability_topic": "homeassistant/switch/transport_test/availability",
            "payload_available": DeviceAvailability.ONLINE.value,
            "payload_not_available": DeviceAvailability.OFFLINE.value,
            "state_topic": "homeassistant/switch/transport_test/state",
            "command_topic": "homeassistant/switch/transport_test/command",
            "object_id": "transport_test",
            "unique_id": "transport_test",
            "device": {
                "name": "Transport Test",
                "identifiers": ["transport_test"],
                "manufacturer": "Hassquitto",
                "model": "MQTT Transport",
            },
        }
    )
    await transport.publish("homeassistant/switch/transport_test/config", message)
    logger.info("Configured device")

    # Subscribe to command topic for switch
    await transport.subscribe("homeassistant/switch/transport_test/command")
    logger.info("Subscribed to topic %s", "homeassistant/switch/transport_test/command")

    # Wait for configuration to be picked up by Home Assistant
    await asyncio.sleep(0.5)

    # Publish availability message
    await transport.publish(
        "homeassistant/switch/transport_test/availability",
        DeviceAvailability.ONLINE.value,
    )
    logger.info("Device is online.")

    # Publish switch state
    for i in range(3):
        await transport.publish(
            "homeassistant/switch/transport_test/state", SwitchState.ON.value
        )
        logger.info("Turned switch on.")
        await asyncio.sleep(3)

        await transport.publish(
            "homeassistant/switch/transport_test/state", SwitchState.OFF.value
        )
        logger.info("Turned switch off.")
        await asyncio.sleep(3)

    # Mark device as unavailable
    await transport.publish(
        "homeassistant/switch/transport_test/availability",
        DeviceAvailability.OFFLINE.value,
    )
    logger.info("Device is offline.")

    # Remove device from Home Assistant
    await asyncio.sleep(1)
    await transport.publish("homeassistant/switch/transport_test/config", "")
    logger.info("Removed device from Home Assistant.")


if __name__ == "__main__":
    # Run main coroutine
    asyncio.run(main())
