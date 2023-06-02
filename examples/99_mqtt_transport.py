import asyncio
import logging
import json

from hassquitto.logging import get_logger
from hassquitto.symbols import DeviceAvailability, SwitchState
from hassquitto.transport import AsyncMQTT


logger = get_logger(__name__)
logger.setLevel(logging.DEBUG)

transport = AsyncMQTT()


@transport.on_connect
async def on_connect(client, userdata, flags, rc):
    logger.info("Connected with result code %s", rc)


@transport.on_message
async def on_message(client, userdata, msg):
    logger.info("Received message on topic %s: %s", msg.topic, msg.payload.decode())


async def main():
    await transport.connect(
        host="homeassistant.local",
        port=1883,
        username="example",
        password="example",
    )
    await asyncio.sleep(1)

    await transport.subscribe("homeassistant/switch/transport_test/command")
    logger.info("Subscribed to topic %s", "homeassistant/switch/transport_test/command")

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

    await asyncio.sleep(1)
    await transport.publish(
        "homeassistant/switch/transport_test/availability",
        DeviceAvailability.ONLINE.value,
    )
    logger.info("Device is online.")

    for i in range(3):
        await asyncio.sleep(3)
        await transport.publish(
            "homeassistant/switch/transport_test/state", SwitchState.ON.value
        )
        logger.info("Turned switch on.")

        await asyncio.sleep(3)
        await transport.publish(
            "homeassistant/switch/transport_test/state", SwitchState.OFF.value
        )
        logger.info("Turned switch off.")

    await asyncio.sleep(1)
    await transport.publish(
        "homeassistant/switch/transport_test/availability",
        DeviceAvailability.OFFLINE.value,
    )
    logger.info("Device is offline.")

    await asyncio.sleep(1)
    await transport.publish("homeassistant/switch/transport_test/config", "")
    logger.info("Removed device from Home Assistant.")


if __name__ == "__main__":
    asyncio.run(main())
