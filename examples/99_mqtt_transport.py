import asyncio
import logging
import json

from hassquitto import validate
from hassquitto.logging import get_logger
from hassquitto.symbols import DeviceAvailability, SwitchState
from hassquitto.transport import AsyncMQTT

# Setup logging
logger = get_logger(__name__)
logger.setLevel(logging.DEBUG)

# Instantiate MQTT transport
transport = AsyncMQTT(client_id="transport_test")


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
    config_topic = validate.topic("homeassistant/switch/transport_test/config")
    availability_topic = validate.topic(
        "homeassistant/switch/transport_test/availability"
    )
    state_topic = validate.topic("homeassistant/switch/transport_test/state")
    command_topic = validate.topic("homeassistant/switch/transport_test/command")

    # Configure switch entity
    message = json.dumps(
        {
            "name": validate.name("Transport Test Switch"),
            "availability_topic": availability_topic,
            "payload_available": DeviceAvailability.ONLINE.value,
            "payload_not_available": DeviceAvailability.OFFLINE.value,
            "state_topic": state_topic,
            "command_topic": command_topic,
            "object_id": validate.object_id("transport_test"),
            "unique_id": validate.unique_id("transport_test"),
            "device": {
                "name": validate.name("Switch"),
                "identifiers": [validate.unique_id("switch")],
                "manufacturer": validate.name("Hassquitto"),
                "model": validate.name("MQTT Switch"),
            },
        }
    )
    await transport.publish(config_topic, message)
    logger.info("Configured device")

    # Subscribe to command topic for switch
    await transport.subscribe(command_topic)
    logger.info("Subscribed to topic %s", command_topic)

    # Wait for configuration to be picked up by Home Assistant
    await asyncio.sleep(1)

    # Publish availability message
    await transport.publish(availability_topic, DeviceAvailability.ONLINE.value)
    logger.info("Device is online.")

    # Publish switch state
    for i in range(3):
        await asyncio.sleep(3)
        await transport.publish(state_topic, SwitchState.ON.value)
        logger.info("Turned switch on.")

        await asyncio.sleep(3)
        await transport.publish(state_topic, SwitchState.OFF.value)
        logger.info("Turned switch off.")

    # Mark device as unavailable
    await asyncio.sleep(1)
    await transport.publish(availability_topic, DeviceAvailability.OFFLINE.value)
    logger.info("Device is offline.")

    # Remove device from Home Assistant
    await asyncio.sleep(1)
    await transport.publish(config_topic, "")
    logger.info("Removed device from Home Assistant.")


if __name__ == "__main__":
    # Run main coroutine
    asyncio.run(main())
